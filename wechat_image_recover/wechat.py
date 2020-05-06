import binascii
import os
import argparse
import datetime

def cal_xor(datpath):
    fh = open(r'test.jpg','rb')
    a = fh.read()
    fh.close()
    hexstr = binascii.b2a_hex(a)
    jpg = hexstr[0:2].decode()
    
    fh = open(datpath,'rb')
    a = fh.read()
    fh.close()
    hexstr = binascii.b2a_hex(a)
    dat = hexstr[0:2].decode()
    
    jpg_16 = int(jpg, 16)
    dat_16 = int(dat, 16)
    return hex(dat_16^jpg_16)
    
def stamp2date(timeStamp):
    dateArray = datetime.datetime.fromtimestamp(timeStamp)
    otherStyleTime = dateArray.strftime("%Y-%m-%d-%H")
    return(otherStyleTime)

def imageDecode(fin,fout,hexnum):
    """
    解码
    :param fin: 微信dat图片路径+名称
    :param fout: 微信图片恢复路径+名称
    :return: 1/0
    """
    # 读取.bat
    dat_read = open(fin,"rb")
    # 图片写入
    img_write = open(fout,"wb")
    # 循环字节
    for now in dat_read:
        for nowByte in now:
            # 转码计算
            newByte = nowByte ^ int(hexnum, 16)
            # 转码后重新写入
            img_write.write(bytes([newByte]))
    dat_read.close()
    img_write.close()

class wechat():
    '''
    一个wechat类代表着一个电脑的wechat图片存放位置的图片管理
    :para path是这个wechat照片的存放点，需要手动设置
    :para time是需要提取的年月的日期
    '''
    def __init__(self, path="D:\\Wechat\\WeChat_Files\\davendw\\FileStorage\\Image\\", time="2019-11", outf="data\\"):
        self.wechat_image_path = path+"\\"+time+"\\"
        self.hexnum = cal_xor(os.path.join(path+"\\"+time+"\\", os.listdir(path+"\\"+time+"\\")[0]))
        self.wechat_recover_path = outf
        self.fsinfo = os.listdir(path+"\\"+time+"\\")
    
    def get_img_list(self, num=10):
        # 把路径文件夹下的文件以列表呈现
        return self.fsinfo[:num]
        
    def img_decoder(self, img_type="jpg", mode="all"):
        # 逐步读取文件
        flag = 0
        for fn in self.fsinfo:
            flag+=1
            # 拼接路径：微信图片路径+日期+图片名
            fn_date = stamp2date(os.path.getctime(os.path.join(self.wechat_image_path,fn)))
            dat_path = os.path.join(self.wechat_image_path,fn)
            # 判断目录还是.bat
            if not os.path.isdir(dat_path):
                print('当前文件：{}+{}'.format(dat_path, fn))
                # 转码函数
                fout = self.wechat_recover_path + fn_date + "-" + fn.replace(".dat","",1) + "." + img_type
                imageDecode(dat_path, fout,self.hexnum)
            else:
                pass
            if mode == "test":
                if flag>10:
                    break
# 运行
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-i', '--in_path', default="E:\\Program Files (x86)\\WeChat\\WeChat_Files\\gl5216\\FileStorage\\Image\\", help='input wechat address')
    parser.add_argument('-o', '--out_path', default="data\\", help='output file folder')
    parser.add_argument('-t', '--time_month', default="2019-11", help='time file')
    parser.add_argument('-m', '--mode', default="all", help='mode')
    args = parser.parse_args()
    in_path = str(args.in_path).replace("_"," ")
    we = wechat(in_path, args.time_month, args.out_path)
    # we.find_img_list()[:10]
    we.img_decoder(img_type="jpg", mode=args.mode)