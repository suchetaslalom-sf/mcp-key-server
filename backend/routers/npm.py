import os
import json
import subprocess
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from security import get_current_active_user, get_current_admin_user
from config import settings

router = APIRouter()


# Utility function to run npm commands
def run_npm_command(command: List[str], cwd: str = None):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd
        )
        return {"success": True, "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": e.stderr}


# Background task to install npm package
def install_npm_package(package_name: str, version: str = None):
    # Create cache directory if it doesn't exist
    os.makedirs(settings.NPM_CACHE_DIR, exist_ok=True)
    
    # Prepare package identifier
    package_identifier = package_name
    if version:
        package_identifier += f"@{version}"
    
    # Run npm install command
    command = ["npm", "install", package_identifier, "--registry", settings.NPM_REGISTRY]
    return run_npm_command(command, cwd=settings.NPM_CACHE_DIR)


@router.post("/packages", response_model=schemas.NpmPackage, status_code=status.HTTP_201_CREATED)
def create_npm_package(package: schemas.NpmPackageCreate,
                       current_user = Depends(get_current_active_user),
                       db: Session = Depends(get_db)):
    # Check if package already exists
    db_package = db.query(models.NpmPackage).filter(
        models.NpmPackage.name == package.name,
        models.NpmPackage.version == package.version,
        models.NpmPackage.owner_id == current_user.id
    ).first()
    
    if db_package:
        raise HTTPException(status_code=400, detail="Package already exists")
    
    # Create new npm package record
    db_package = models.NpmPackage(
        name=package.name,
        version=package.version,
        description=package.description,
        is_private=package.is_private,
        package_json=package.package_json,
        owner_id=current_user.id
    )
    db.add(db_package)
    db.commit()
    db.refresh(db_package)
    return db_package


@router.get("/packages", response_model=List[schemas.NpmPackage])
def get_npm_packages(name: Optional[str] = None,
                     is_private: Optional[bool] = None,
                     current_user = Depends(get_current_active_user),
                     db: Session = Depends(get_db)):
    # Query packages owned by current user
    query = db.query(models.NpmPackage).filter(models.NpmPackage.owner_id == current_user.id)
    
    # Apply filters if provided
    if name:
        query = query.filter(models.NpmPackage.name.like(f"%{name}%"))
    if is_private is not None:
        query = query.filter(models.NpmPackage.is_private == is_private)
    
    return query.all()


@router.get("/packages/{package_id}", response_model=schemas.NpmPackage)
def get_npm_package(package_id: int,
                    current_user = Depends(get_current_active_user),
                    db: Session = Depends(get_db)):
    # Query specific package
    db_package = db.query(models.NpmPackage).filter(models.NpmPackage.id == package_id).first()
    
    # Check if package exists and belongs to the current user
    if db_package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    if db_package.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this package")
    
    return db_package


@router.put("/packages/{package_id}", response_model=schemas.NpmPackage)
def update_npm_package(package_id: int,
                       package_update: schemas.NpmPackageUpdate,
                       current_user = Depends(get_current_active_user),
                       db: Session = Depends(get_db)):
    # Query specific package
    db_package = db.query(models.NpmPackage).filter(models.NpmPackage.id == package_id).first()
    
    # Check if package exists and belongs to the current user
    if db_package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    if db_package.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this package")
    
    # Update package fields if provided
    if package_update.version is not None:
        db_package.version = package_update.version
    if package_update.description is not None:
        db_package.description = package_update.description
    if package_update.is_private is not None:
        db_package.is_private = package_update.is_private
    if package_update.package_json is not None:
        db_package.package_json = package_update.package_json
    
    db.commit()
    db.refresh(db_package)
    return db_package


@router.delete("/packages/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_npm_package(package_id: int,
                       current_user = Depends(get_current_active_user),
                       db: Session = Depends(get_db)):
    # Query specific package
    db_package = db.query(models.NpmPackage).filter(models.NpmPackage.id == package_id).first()
    
    # Check if package exists and belongs to the current user
    if db_package is None:
        raise HTTPException(status_code=404, detail="Package not found")
    if db_package.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this package")
    
    # Delete the package
    db.delete(db_package)
    db.commit()
    return None


@router.post("/install", status_code=status.HTTP_202_ACCEPTED)
def install_package(package_name: str,
                    version: Optional[str] = None,
                    background_tasks: BackgroundTasks = None,
                    current_user = Depends(get_current_active_user)):
    # Add npm install task to background tasks
    if background_tasks:
        background_tasks.add_task(install_npm_package, package_name, version)
        return {"message": f"Installation of {package_name} started in the background"}
    else:
        # If background tasks not available, run synchronously
        result = install_npm_package(package_name, version)
        if result["success"]:
            return {"message": f"Successfully installed {package_name}"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to install package: {result['error']}")


@router.get("/installed", response_model=List[dict])
def list_installed_packages(current_user = Depends(get_current_active_user)):
    # Check if npm cache directory exists
    if not os.path.exists(settings.NPM_CACHE_DIR):
        return []
    
    # Get package.json file path
    package_json_path = os.path.join(settings.NPM_CACHE_DIR, "package.json")
    
    if not os.path.exists(package_json_path):
        return []
    
    # Read package.json to get installed packages
    try:
        with open(package_json_path, "r") as f:
            package_data = json.load(f)
        
        dependencies = package_data.get("dependencies", {})
        dev_dependencies = package_data.get("devDependencies", {})
        
        # Format response
        installed_packages = []
        
        for name, version in dependencies.items():
            installed_packages.append({"name": name, "version": version, "dev": False})
        
        for name, version in dev_dependencies.items():
            installed_packages.append({"name": name, "version": version, "dev": True})
        
        return installed_packages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read package.json: {str(e)}")
