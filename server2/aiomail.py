import os
import aiosmtplib
import logging
from typing import List, Optional
from email.message import EmailMessage
from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

class EmailSender:
    def __init__(
        self, 
        email_address: Optional[str] = None, 
        email_password: Optional[str] = None, 
        smtp_server: Optional[str] = None, 
        smtp_port: Optional[int] = None, 
        log_file_path: Optional[str] = None
    ) -> None:
        """
        Инициализация отправителя для Mail.ru.

        :param email_address: Email-адрес отправителя на Mail.ru
        :param email_password: Пароль от почты Mail.ru
        :param smtp_server: SMTP сервер Mail.ru
        :param smtp_port: Порт SMTP Mail.ru
        :param log_file_path: Путь к файлу логов
        """
        # Берем значения из параметров или из .env файла
        self.email_address = email_address or os.getenv('EMAIL_ADDRESS')
        self.email_password = email_password or os.getenv('EMAIL_PASSWORD')
        
        # Для Mail.ru используем smtp.mail.ru
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.mail.ru')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', 587))
        self.log_file_path = log_file_path or os.getenv('LOG_FILE_PATH')

        print("=" * 50)
        print("🚀 EMAIL SENDER ДЛЯ MAIL.RU")
        print("=" * 50)
        print(f"📧 Отправитель: {self.email_address}")
        print(f"🔗 SMTP сервер: {self.smtp_server}:{self.smtp_port}")
        print(f"🔐 Пароль: {'*' * len(self.email_password) if self.email_password else 'Не указан'}")
        print("=" * 50)

        # Валидация обязательных параметров
        if not all([self.email_address, self.email_password]):
            missing = []
            if not self.email_address: missing.append('EMAIL_ADDRESS')
            if not self.email_password: missing.append('EMAIL_PASSWORD')
            raise ValueError(f"Отсутствуют обязательные параметры: {missing}")

        self._setup_logging()

    def _setup_logging(self) -> None:
        """Настройка логирования."""
        self.logger = logging.getLogger(__name__)
        
        # Если логгер уже настроен, не настраиваем повторно
        if self.logger.handlers:
            return

        self.logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Консольный handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Файловый handler (если указан путь)
        if self.log_file_path:
            log_dir = os.path.dirname(self.log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_handler = logging.FileHandler(self.log_file_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    async def send_email(
        self, 
        subject: str, 
        body: str, 
        recipients: List[str], 
        sender: Optional[str] = None,
        is_html: bool = False
    ) -> bool:
        """
        Отправляет email сообщение через Mail.ru.

        :param subject: Тема письма.
        :param body: Текст письма.
        :param recipients: Список получателей.
        :param sender: Адрес отправителя (по умолчанию используется email_address).
        :param is_html: Если True, тело письма будет интерпретироваться как HTML.
        :return: True если отправка успешна, False в случае ошибки.
        """
        if not recipients:
            self.logger.error("Список получателей не может быть пустым")
            return False

        sender = sender or self.email_address

        # Создаём EmailMessage
        message = EmailMessage()
        message["From"] = sender
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject
        
        # Устанавливаем содержимое (HTML или plain text)
        if is_html:
            message.set_content(body, subtype="html")
        else:
            message.set_content(body)

        try:
            self.logger.info(f"🔄 Подключение к Mail.ru SMTP...")
            
            # Отправка сообщения через Mail.ru SMTP
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                username=self.email_address,
                password=self.email_password,
                start_tls=True,
                timeout=30
            )
            
            self.logger.info(f"✅ Сообщение отправлено через Mail.ru! Тема: '{subject}'")
            return True
            
        except aiosmtplib.SMTPAuthenticationError as e:
            self.logger.error(f"❌ Ошибка аутентификации Mail.ru: {e}")
            self.logger.info("💡 Проверьте правильность email и пароля от Mail.ru")
            return False
        except aiosmtplib.SMTPConnectError as e:
            self.logger.error(f"❌ Ошибка подключения к Mail.ru SMTP: {e}")
            return False
        except aiosmtplib.SMTPTimeoutError as e:
            self.logger.error(f"❌ Таймаут при отправке письма: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Ошибка при отправке письма: {e}")
            return False

    async def send_html_email(
        self, 
        subject: str, 
        html_body: str, 
        recipients: List[str], 
        sender: Optional[str] = None
    ) -> bool:
        """
        Отправляет HTML email сообщение через Mail.ru.

        :param subject: Тема письма.
        :param html_body: HTML содержимое письма.
        :param recipients: Список получателей.
        :param sender: Адрес отправителя.
        :return: True если отправка успешна, False в случае ошибки.
        """
        return await self.send_email(subject, html_body, recipients, sender, is_html=True)

    def test_connection(self) -> bool:
        """
        Проверяет базовую конфигурацию Mail.ru.

        :return: True если конфигурация корректна.
        """
        if not self.email_address:
            self.logger.error("❌ EMAIL_ADDRESS не указан")
            return False
        
        if not self.email_password:
            self.logger.error("❌ EMAIL_PASSWORD не указан")
            return False
        
        self.logger.info(f"✅ Конфигурация Mail.ru корректна: {self.smtp_server}:{self.smtp_port}")
        return True


# Пример использования с Mail.ru
async def example_usage():
    """
    Пример использования EmailSender с Mail.ru
    """
    try:
        print("🎯 ПРИМЕР ИСПОЛЬЗОВАНИЯ MAIL.RU")
        
        # Способ 1: Через параметры конструктора
        email_sender = EmailSender(
            email_address="mpitrassylka@mail.ru",
            email_password="your_mailru_password",
            smtp_server="smtp.mail.ru",
            smtp_port=587,
            log_file_path="logs/mailru_email.log"
        )
        
        # Проверка конфигурации
        if not email_sender.test_connection():
            return
        
        # Отправка тестового письма
        success = await email_sender.send_email(
            subject="Тест Mail.ru - Hello World!",
            body="""Привет! Это тестовое письмо отправлено через Mail.ru SMTP.

📧 От: mpitrassylka@mail.ru
🔗 Через: smtp.mail.ru:587
✅ Успешная отправка!

Если вы это читаете - Mail.ru работает отлично!""",
            recipients=["agmertema@mail.ru"]
        )
        
        if success:
            print("🎉 Тестовое письмо успешно отправлено через Mail.ru!")
        else:
            print("❌ Не удалось отправить письмо через Mail.ru")
            
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())