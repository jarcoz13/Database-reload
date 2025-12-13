"""
Alert Checker Job
Verifica las alertas activas y envía notificaciones cuando se cumplen las condiciones
Se ejecuta cada minuto para verificar lecturas recientes
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database.postgres_db import SessionLocal
from models import Alert, AirQualityReading, Station, Pollutant, AppUser
from services.telegram_notifier import get_telegram_notifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertCheckerJob:
    """
    Job que verifica alertas activas contra lecturas recientes
    y dispara notificaciones cuando se cumplen las condiciones
    """
    
    def __init__(self):
        self.telegram = get_telegram_notifier()
        self.last_notifications = {}  # Track para evitar spam
    
    async def run(self):
        """Main execution method"""
        logger.info("Starting alert checker job...")
        start_time = datetime.utcnow()
        
        db = SessionLocal()
        try:
            # Obtener todas las alertas activas
            active_alerts = db.query(Alert).filter(Alert.is_active == True).all()
            
            if not active_alerts:
                logger.info("No active alerts to check")
                return
            
            logger.info(f"Checking {len(active_alerts)} active alerts")
            
            notifications_sent = 0
            
            # Verificar cada alerta
            for alert in active_alerts:
                try:
                    if await self._check_and_notify_alert(db, alert):
                        notifications_sent += 1
                except Exception as e:
                    logger.error(f"Error checking alert {alert.id}: {str(e)}")
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Alert checker completed in {duration:.2f}s. Sent {notifications_sent} notifications.")
            
        except Exception as e:
            logger.error(f"Fatal error in alert checker: {str(e)}")
            raise
        finally:
            db.close()
    
    async def _check_and_notify_alert(
        self,
        db: Session,
        alert: Alert
    ) -> bool:
        """
        Verifica una alerta específica y envía notificación si aplica
        
        Returns:
            True si se envió notificación, False otherwise
        """
        # Obtener la lectura más reciente para esta estación y contaminante
        recent_reading = db.query(AirQualityReading).filter(
            and_(
                AirQualityReading.station_id == alert.station_id,
                AirQualityReading.pollutant_id == alert.pollutant_id,
                AirQualityReading.datetime >= datetime.utcnow() - timedelta(minutes=5)
            )
        ).order_by(AirQualityReading.datetime.desc()).first()
        
        if not recent_reading:
            logger.debug(f"No recent reading for alert {alert.id}")
            return False
        
        # Verificar si se cumple la condición
        if not self._check_condition(
            recent_reading.value,
            alert.threshold,
            alert.trigger_condition
        ):
            logger.debug(f"Alert {alert.id} condition not met")
            return False
        
        # Verificar cooldown para evitar spam (no notificar más de 1 vez cada 30 min)
        alert_key = f"{alert.id}_{alert.station_id}_{alert.pollutant_id}"
        last_notif_time = self.last_notifications.get(alert_key)
        
        if last_notif_time:
            time_since_last = (datetime.utcnow() - last_notif_time).total_seconds()
            if time_since_last < 1800:  # 30 minutos
                logger.debug(f"Alert {alert.id} in cooldown period")
                return False
        
        # Enviar notificación
        sent = await self._send_alert_notification(db, alert, recent_reading)
        
        if sent:
            self.last_notifications[alert_key] = datetime.utcnow()
            
            # Actualizar timestamp de última notificación (si agregas este campo al modelo)
            # alert.last_notification_at = datetime.utcnow()
            # db.commit()
        
        return sent
    
    def _check_condition(
        self,
        value: float,
        threshold: float,
        condition: str
    ) -> bool:
        """Verifica si se cumple la condición de la alerta"""
        if condition == 'exceeds':
            return value > threshold
        elif condition == 'below':
            return value < threshold
        elif condition == 'equals':
            return abs(value - threshold) < 0.01
        else:
            logger.warning(f"Unknown condition: {condition}")
            return False
    
    async def _send_alert_notification(
        self,
        db: Session,
        alert: Alert,
        reading: AirQualityReading
    ) -> bool:
        """Envía notificación de alerta"""
        
        # Obtener información adicional
        station = db.query(Station).filter(Station.id == alert.station_id).first()
        pollutant = db.query(Pollutant).filter(Pollutant.id == alert.pollutant_id).first()
        user = db.query(AppUser).filter(AppUser.id == alert.user_id).first()
        
        if not station or not pollutant:
            logger.error(f"Missing station or pollutant for alert {alert.id}")
            return False
        
        alert_data = {
            'station_name': f"{station.name} - {station.city}",
            'pollutant_name': pollutant.name,
            'threshold': alert.threshold,
            'trigger_condition': alert.trigger_condition,
            'user_name': user.full_name if user else 'Unknown User'
        }
        
        reading_data = {
            'value': reading.value,
            'aqi': reading.aqi,
            'datetime': reading.datetime
        }
        
        # Enviar según método de notificación
        notification_sent = False
        
        if alert.notification_method in ['telegram', 'all']:
            try:
                notification_sent = await self.telegram.send_alert(alert_data, reading_data)
                logger.info(f"Telegram notification sent for alert {alert.id}")
            except Exception as e:
                logger.error(f"Failed to send Telegram notification: {str(e)}")
        
        if alert.notification_method in ['email', 'all']:
            # TODO: Implementar notificación por email
            logger.info(f"Email notification would be sent for alert {alert.id}")
        
        if alert.notification_method == 'in-app':
            # TODO: Guardar notificación in-app en base de datos
            logger.info(f"In-app notification would be created for alert {alert.id}")
        
        return notification_sent


async def main():
    """Entry point para ejecución directa o testing"""
    job = AlertCheckerJob()
    await job.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
