import logging
import sys

class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[1;31m', # 加粗红色
        'RESET': '\033[0m',       # 重置颜色
    }

    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)
        self.use_colors = sys.stdout.isatty()

    def format(self, record):
        log_message = super().format(record)
        if self.use_colors:
            color_code = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            return f"{color_code}{log_message}{self.COLORS['RESET']}"
        return log_message

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器。

    Args:
        name (str): 日志记录器的名称。

    Returns:
        logging.Logger: 日志记录器对象。
    """
    logger = logging.getLogger(name)

    console_handler = logging.StreamHandler()

    formatter = ColorFormatter(
        '%(asctime)s - %(name)s - %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
