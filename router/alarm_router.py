from fastapi import FastAPI, HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from data.database import get_alarmdb
from data.models import Alarm
from data.schema import CreateDeviceToken,DeviceToken,AlarmInfo
router = APIRouter()


@router.post("/api/device-token", response_model=DeviceToken, tags=["alarm"])
async def receive_device_token(device_token: CreateDeviceToken, db: Session = Depends(get_alarmdb)):
    db_token = db.query(Alarm).filter(Alarm.device_token == device_token.device_token).first()
    if db_token:
        raise HTTPException(status_code=400, detail="Device token already exists")
    
    new_token = Alarm(
        device_token=device_token.device_token,
        check_totalcouncil=True,
        check_departcouncil=True,
        check_depart=True,
        check_apply=True
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    return {"device_token": device_token.device_token}

@router.get("/api/get_alarm_status", response_model= AlarmInfo, tags=["alarm"])
async def show_alarm_status(token: str, db: Session = Depends(get_alarmdb)):
    db_info = db.query(Alarm).filter(Alarm.device_token == token).first()
    if not db_info:
        raise HTTPException(status_code=404, detail="토큰존재하지않음")
    return {"check_totalcouncil": db_info.check_totalcouncil,"check_departcouncil": db_info.check_departcouncil,"check_depart": db_info.check_depart,"check_apply": db_info.check_apply}

@router.patch("/api/update_alarm_status",tags=["alarm"])
async def change_alarm_status(alarm_info: CreateDeviceToken, db: Session = Depends(get_alarmdb)):
    db_info = db.query(Alarm).filter(Alarm.device_token == alarm_info.device_token).first()
    db_info.check_totalcouncil = alarm_info.check_totalcouncil
    db_info.check_departcouncil = alarm_info.check_departcouncil
    db_info.check_depart = alarm_info.check_depart
    db_info.check_apply = alarm_info.check_apply
    db.commit()
    db.refresh(db_info)
    return HTTPException(status_code=200, detail="정상적으로 알람설정이 완료되었습니다.")