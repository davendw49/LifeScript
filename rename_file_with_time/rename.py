import os
import argparse
import datetime
from shutil import copyfile

def stamp2date(timeStamp):
    dateArray = datetime.datetime.fromtimestamp(timeStamp)
    otherStyleTime = dateArray.strftime("%Y-%m-%d-%H")
    return(otherStyleTime)

class rnpool():
    '''
        一个rnpool类代表着一个电脑的文件存放位置
        :para inpath是这个文件的存放点，需要手动设置
        :para outpath是这个文件的改名之后的存放点，需要手动设置
    '''

    def __init__(self, inpath=".", outpath="data\\"):
        self.rnpool_inpath = inpath
        self.rnpool_outpath = outpath
        self.fsinfo = os.listdir(inpath + "\\")

    def rename(self, mode="all"):
        # 逐步读取文件
        flag = 0
        for fn in self.fsinfo:
            flag += 1
            # 拼接路径：微信图片路径+日期+图片名
            fn_date = stamp2date(os.path.getctime(os.path.join(self.rnpool_inpath, fn)))
            copyfile(os.path.join(self.rnpool_inpath, fn), os.path.join(self.rnpool_outpath, fn_date + "-" + fn))

            if mode == "test":
                if flag > 10:
                    break

# 运行
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', '--in_path', default=".\\test\\", help='input wechat address')
    parser.add_argument('-o', '--out_path', default="data\\", help='output file folder')
    parser.add_argument('-m', '--mode', default="all", help='mode')
    args = parser.parse_args()
    in_path = str(args.in_path).replace("_"," ")
    rp = rnpool(in_path, args.out_path)
    rp.rename(mode=args.mode)