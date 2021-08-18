import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

# ロガーインスタンス取得
logger = logging.getLogger(__name__)

# ログレベル別関数
loglevel_funcs = {
    'DEBUG':logger.debug,
    'INFO':logger.info,
    'WARNING':logger.warning,
    'ERROR':logger.error,
    'CRITICAL':logger.critical
}

# 出力レベルの下限を設定
logger.setLevel(os.getenv('LOG_LEVEL'))

# コンソール出力設定
sh = logging.StreamHandler()
logger.addHandler(sh)

# ファイル出力設定
logfile_name = datetime.now().strftime('%Y%m%d_%H%M%S')
fh = logging.FileHandler(f'{logfile_name}.log')
logger.addHandler(fh)

# ログ形式設定
formatter = logging.Formatter('[%(asctime)s(%(process)d)] <%(levelname)s> %(message)s')
sh.setFormatter(formatter)
fh.setFormatter(formatter)


# ログ出力
def writelog(level, text):
    loglevel_funcs[level](text)

