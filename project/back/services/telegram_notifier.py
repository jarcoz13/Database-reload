"""
Telegram Notification Service
Sends air quality alerts to Telegram groups/channels
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio

try:
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logging.warning("python-telegram-bot not installed. Telegram notifications disabled.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Service for sending notifications via Telegram"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = TELEGRAM_AVAILABLE and self.bot_token and self.chat_id
        
        if not TELEGRAM_AVAILABLE:
            logger.warning("Telegram notifications disabled: python-telegram-bot not installed")
        elif not self.bot_token:
            logger.warning("Telegram notifications disabled: TELEGRAM_BOT_TOKEN not configured")
        elif not self.chat_id:
            logger.warning("Telegram notifications disabled: TELEGRAM_CHAT_ID not configured")
        else:
            self.bot = Bot(token=self.bot_token)
            logger.info(f"Telegram notifier initialized for chat {self.chat_id}")
    
    async def send_alert(
        self,
        alert_data: Dict[str, Any],
        reading_data: Dict[str, Any]
    ) -> bool:
        """
        Send an air quality alert to Telegram
        
        Args:
            alert_data: Dictionary with alert information
            reading_data: Dictionary with current reading that triggered alert
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Telegram notifications disabled, skipping alert")
            return False
        
        try:
            message = self._format_alert_message(alert_data, reading_data)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"Alert sent to Telegram: {alert_data.get('station_name')} - {alert_data.get('pollutant_name')}")
            return True
            
        except TelegramError as e:
            logger.error(f"Failed to send Telegram alert: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram alert: {str(e)}")
            return False
    
    async def send_daily_summary(
        self,
        summary_data: Dict[str, Any]
    ) -> bool:
        """
        Send a daily air quality summary to Telegram
        
        Args:
            summary_data: Dictionary with daily statistics
            
        Returns:
            True if message sent successfully
        """
        if not self.enabled:
            return False
        
        try:
            message = self._format_summary_message(summary_data)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )
            logger.info("Daily summary sent to Telegram")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send daily summary: {str(e)}")
            return False
    
    def _format_alert_message(
        self,
        alert_data: Dict[str, Any],
        reading_data: Dict[str, Any]
    ) -> str:
        """Format alert data into a Telegram message"""
        
        station_name = alert_data.get('station_name', 'Unknown Station')
        pollutant_name = alert_data.get('pollutant_name', 'Unknown Pollutant')
        threshold = alert_data.get('threshold', 0)
        current_value = reading_data.get('value', 0)
        aqi = reading_data.get('aqi', 0)
        condition = alert_data.get('trigger_condition', 'exceeds')
        
        # Determinar emoji según el nivel de AQI
        emoji = self._get_aqi_emoji(aqi)
        
        # Determinar severidad
        severity = self._get_severity_level(aqi)
        
        message = f"""
🚨 <b>ALERTA DE CALIDAD DEL AIRE</b> {emoji}

📍 <b>Estación:</b> {station_name}
🧪 <b>Contaminante:</b> {pollutant_name}

📊 <b>Valores Actuales:</b>
• Concentración: {current_value:.2f}
• AQI: {aqi}
• Umbral: {threshold}
• Condición: {self._translate_condition(condition)}

⚠️ <b>Nivel:</b> {severity}

🕐 <b>Hora:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 <b>Recomendación:</b>
{self._get_health_recommendation(aqi)}

🌍 Air Quality Monitor - Jarcoz System
"""
        return message.strip()
    
    def _format_summary_message(self, summary_data: Dict[str, Any]) -> str:
        """Format daily summary into a Telegram message"""
        
        date = summary_data.get('date', datetime.now().strftime('%Y-%m-%d'))
        total_readings = summary_data.get('total_readings', 0)
        avg_aqi = summary_data.get('avg_aqi', 0)
        max_aqi = summary_data.get('max_aqi', 0)
        stations_data = summary_data.get('stations', [])
        
        emoji = self._get_aqi_emoji(avg_aqi)
        
        message = f"""
📊 <b>RESUMEN DIARIO - CALIDAD DEL AIRE</b> {emoji}

📅 <b>Fecha:</b> {date}
📈 <b>Lecturas Totales:</b> {total_readings}

<b>Índices de Calidad del Aire:</b>
• AQI Promedio: {avg_aqi:.1f}
• AQI Máximo: {max_aqi}

<b>Estado por Estación:</b>
"""
        
        for station in stations_data[:5]:  # Limitar a 5 estaciones
            name = station.get('name', 'Unknown')
            aqi = station.get('avg_aqi', 0)
            emoji_st = self._get_aqi_emoji(aqi)
            message += f"\n{emoji_st} {name}: AQI {aqi:.1f}"
        
        message += "\n\n🌍 Air Quality Monitor - Jarcoz System"
        
        return message.strip()
    
    def _get_aqi_emoji(self, aqi: float) -> str:
        """Get emoji based on AQI level"""
        if aqi <= 50:
            return "🟢"  # Good
        elif aqi <= 100:
            return "🟡"  # Moderate
        elif aqi <= 150:
            return "🟠"  # Unhealthy for Sensitive
        elif aqi <= 200:
            return "🔴"  # Unhealthy
        elif aqi <= 300:
            return "🟣"  # Very Unhealthy
        else:
            return "🟤"  # Hazardous
    
    def _get_severity_level(self, aqi: float) -> str:
        """Get severity description based on AQI"""
        if aqi <= 50:
            return "Bueno ✅"
        elif aqi <= 100:
            return "Moderado ⚠️"
        elif aqi <= 150:
            return "Dañino para Grupos Sensibles 🔶"
        elif aqi <= 200:
            return "Dañino 🔴"
        elif aqi <= 300:
            return "Muy Dañino ⛔"
        else:
            return "Peligroso ☠️"
    
    def _get_health_recommendation(self, aqi: float) -> str:
        """Get health recommendation based on AQI"""
        if aqi <= 50:
            return "La calidad del aire es satisfactoria. Disfrute de actividades al aire libre."
        elif aqi <= 100:
            return "Calidad del aire aceptable. Personas sensibles deben considerar limitar actividades prolongadas."
        elif aqi <= 150:
            return "Grupos sensibles pueden experimentar efectos. Reduzca esfuerzos prolongados al aire libre."
        elif aqi <= 200:
            return "Todos pueden experimentar efectos. Limite el tiempo al aire libre."
        elif aqi <= 300:
            return "Alerta de salud: todos deben evitar esfuerzos al aire libre."
        else:
            return "Emergencia de salud: permanezca en interiores con ventanas cerradas."
    
    def _translate_condition(self, condition: str) -> str:
        """Translate trigger condition to Spanish"""
        translations = {
            'exceeds': 'supera',
            'below': 'está por debajo de',
            'equals': 'es igual a'
        }
        return translations.get(condition, condition)
    
    async def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        if not self.enabled:
            logger.warning("Cannot test connection: Telegram not enabled")
            return False
        
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"Telegram bot connected: @{bot_info.username}")
            
            # Send test message
            await self.bot.send_message(
                chat_id=self.chat_id,
                text="✅ Bot de Air Quality Monitor conectado exitosamente!"
            )
            return True
            
        except Exception as e:
            logger.error(f"Telegram connection test failed: {str(e)}")
            return False


# Singleton instance
_notifier_instance = None

def get_telegram_notifier() -> TelegramNotifier:
    """Get or create Telegram notifier singleton"""
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = TelegramNotifier()
    return _notifier_instance


async def main():
    """Test the Telegram notifier"""
    notifier = get_telegram_notifier()
    
    if notifier.enabled:
        # Test connection
        await notifier.test_connection()
        
        # Test alert
        test_alert = {
            'station_name': 'Kennedy - Bogotá',
            'pollutant_name': 'PM2.5',
            'threshold': 50,
            'trigger_condition': 'exceeds'
        }
        
        test_reading = {
            'value': 75.5,
            'aqi': 125
        }
        
        await notifier.send_alert(test_alert, test_reading)
    else:
        logger.error("Telegram notifier not enabled. Check configuration.")


if __name__ == "__main__":
    asyncio.run(main())
