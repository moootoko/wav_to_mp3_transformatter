import os
import glob
import pydub
import multiprocessing
import logging
import logging.config
from datetime import datetime

# ログ設定インポート
logging.config.fileConfig('logging.conf')

# logger取得
logger = logging.getLogger()

# ログレベル別関数
loglevel_funcs = {
    'DEBUG':logger.debug,
    'INFO':logger.info,
    'WARNING':logger.warning,
    'ERROR':logger.error,
    'CRITICAL':logger.critical
}


# ログ出力
def writelog(level, text):
    loglevel_funcs[level](text)


# wavからmp3へ変換
def trans_wav_to_mp3(wavpath):
    mp3path = wavpath.replace('.wav', '.mp3')
    wavname = '/'.join(wavpath.split('/')[6:])
    mp3name = '/'.join(mp3path.split('/')[6:])
    sound = pydub.AudioSegment.from_wav(wavpath)
    result = True

    writelog('INFO', f'Start transforming: {wavname}')

    try:
        sound.export(mp3path, format='mp3')
    except Exception as e:
        writelog('ERROR', 'Failed to transform for below cause.')
        writelog('ERROR', e)
        result = False
    else:
        writelog('INFO', f'Finish transforming: {wavname} -> {mp3name}')
    finally:
        del sound
        return { 'filename':wavname, 'result':result }


# メイン
if __name__ == '__main__':
    # 変換元ファイル名のリスト
    wavpath_list = glob.glob(
            'wav格納先/**/*.wav',
            recursive=True
    )
    # 変換結果
    result = list()

    writelog('INFO', f'## Start {__file__} ##')

    # 4プロセス並行で変換実行
    with multiprocessing.Pool(4) as p:
        result = p.map(trans_wav_to_mp3, wavpath_list)

    # 失敗件数とファイル名を表示
    failed_list = [d for d in result if d.get('result')==False]
    failed_count = len(failed_list)
    if failed_count > 0:
        writelog('WARNING', f'{failed_count} files couldn\'t be transformed.')
        for fd in failed_list:
            writelog('WARNING', d.get('filename'))
    else:
        writelog('INFO', 'Successfully completed.')

    writelog('INFO', f'## End {__file__} ##')
