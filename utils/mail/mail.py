import logging
import os
import smtplib
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mimetypes import guess_type


class MailSender:

    def __init__(self, logger):
        self.logger = logger
        self.toaddr = []
        self.cc = []
        self.bcc = []
        self.fromaddr = ""
        self.password = ""
        self.smtp = ""
        self.port = ''

    def send(self, subject, body, emails_to_send, attachments=None):
        try:
            if emails_to_send is None:
                self.logger.error("Nenhum email como destinatário!")
                self.logger.error("O email não será enviado")
                return

            for email_to_send in emails_to_send:
                if email_to_send not in self.toaddr:
                    self.toaddr.append(email_to_send)
            emails_to_send = ', '.join(self.toaddr)
            self.logger.debug(f"Destinatários: {emails_to_send}")

            msg = MIMEMultipart()
            msg['From'] = self.fromaddr
            msg['To'] = emails_to_send
            msg['CC'] = ', '.join(self.cc)
            msg['BCC'] = ', '.join(self.bcc)
            msg['Subject'] = subject

            part = MIMEText(body, 'html')
            msg.attach(part)

            if attachments is not None:
                self.logger.debug("Há arquivos para serem anexados")
                self.logger.debug(f"Arquivos: {str(attachments)}")
                for filename in attachments:
                    mimetype, encoding = guess_type(filename)
                    mimetype = mimetype.split('/', 1)
                    fp = open(filename, 'rb')
                    attachment = MIMEBase(mimetype[0], mimetype[1])
                    attachment.set_payload(fp.read())
                    fp.close()
                    encode_base64(attachment)
                    attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filename))
                    msg.attach(attachment)

            self.logger.info("Enviando email")

            server = smtplib.SMTP(self.smtp, self.port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.fromaddr, self.password)
            server.sendmail(self.fromaddr, self.toaddr + self.cc + self.bcc, msg.as_string())
            server.quit()

            self.logger.info("Email enviado")
        except Exception as e:
            self.logger.error("Ocorreu um erro ao enviar o email")
            self.logger.error(str(e))


if __name__ == "__main__":
    # Somente para testes
    test_logger = logging.getLogger('mail-sending-utils')
    email = MailSender(test_logger)
    test_subject = "Assunto do email de teste"
    test_body = "Corpo do email de teste"
    email.send(test_subject, test_body, ['seuemail@blabla.com'])
