import os
import sys
import glob
import subprocess
import multiprocessing
import logging
import logging.config
from dotenv import load_dotenv
from mylogging import *


# wavからmp3へ変換
def trans_wav_to_mp3(wavpath):
    mp3path = wavpath.replace('.wav', '.mp3')
    wavname = '/'.join(wavpath.split('/')[6:])
    mp3name = '/'.join(mp3path.split('/')[6:])
    size = os.path.getsize(wavpath)
    result = True

    writelog('INFO', f'Start transforming: {wavname} ({size:,} Byte)')

    try:
        # ffmpegを直接使用して変換
        # 強制上書き, ログレベル:error
        subprocess.call(f'ffmpeg -i {wavpath} -y -loglevel error {mp3path}', shell=True)
    except FileNotFoundError as fnfe:
        writelog('ERROR', f'File not found. Please check the path.')
        result = False
    except Exception as e: 
        # 変換失敗
        writelog('ERROR', f'Failed to transform {wavname} : {e}')
        result = False
    else:
        # 変換成功
        writelog('INFO', f'Finish transforming: {wavname} -> {mp3name}')
    
    return { 'filename':wavpath, 'result':result }


# ファイルを削除
def delfile(file_list):
    writelog('INFO', 'Remove transformed wav files...')
    writelog('DEBUG', file_list)

    for filepath in file_list:
        filename = '/'.join(filepath.split('/')[6:])
        try:
            os.remove(filepath)
        except Exception as e:
            writelog('ERROR', f'Failed to remove {filename} : {e}')
        else:
            writelog('INFO', f'Removed {filename}')



# メイン
if __name__ == '__main__':
    # コマンドライン引数チェック
    args = sys.argv
    if len(args) != 3:
        # 引数の個数が不正
        print('Two argument must be specified: python exec.py [FileNum] [ProcessNum]')
        sys.exit()
    if not args[1].isdigit() or int(args[1]) < 0:
        # ファイル数が0以上の整数でない場合
        print('First argument must be an integers which is equal to or greater than 0.')
        sys.exit()
    if not args[2].isdigit() or int(args[2]) < 1:
        # プロセス数が1以上の整数でない場合
        print('Second argument must be an integer which is equal to or greater than 1.')
        sys.exit()

    # 開始ログ
    writelog('INFO', f'## Start {__file__} ##')
    
    # 環境変数をロード
    load_dotenv()

    # 変換ファイル数
    transnum = int(args[1])
    # プロセス数
    processnum = int(args[2])
    # 音源配置ディレクトリ
    sound_dir = os.getenv('SOUND_DIR')
    writelog('DEBUG', f'sound root directory : {sound_dir}')
    sound_dir += '**/*.wav'
    # 音源ファイル名のリスト
    wavpath_list = glob.glob(sound_dir, recursive=True)
    if transnum != 0:
        wavpath_list = wavpath_list[:transnum]
    writelog('DEBUG', f'the number of files : {len(wavpath_list)}')
    # 変換結果
    result = list()

    # 変換開始
    s_transnum = 'all' if transnum == 0 else str(transnum)
    writelog('INFO', f'Start transforming {s_transnum} files on {processnum} processes.')
    with multiprocessing.Pool(processnum) as p:
        result = p.map(trans_wav_to_mp3, wavpath_list)

    # 失敗件数とファイル名を表示
    failed_list = [d.get('filename') for d in result if d.get('result')==False]
    failed_count = len(failed_list)
    if failed_count > 0:
        writelog('WARNING', f'{failed_count} files couldn\'t be transformed.')
        for fname in failed_list:
            writelog('WARNING', fname)
    else:
        writelog('INFO', 'Successfully completed transforming.')

    # 変換したwavファイルを削除（失敗したファイルは削除しない）
    success_list = [d.get('filename') for d in result if d.get('result')==True]
    delfile(success_list)

    # 終了ログ
    writelog('INFO', f'## End {__file__} ##')
