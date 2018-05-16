import matplotlib.image as mpimg
import numpy as np
from scipy.stats import mode
import argparse

#应该有很多地方可以用 any() 和 all() 简化

#四个数相加 大于一个阈值 则为白色[1,1,1,1] <另一个阈值 则为透明（0,0,0,0） 另一种情况 则为背景色
#像素种类很多 思路一 怕是无法实现
#方法一 除了白色和透明的  其他分两组，每组不同的颜色
#方法二  虽然像素种类很多 ，但是看它们的差距给他们分组

# area 周围几个像素不改
#**本程序为img[x,y,z]

#默认参数
PATH = 'html.png'

def write_transparent(img):
    """
    将图片中的白色和透明部分的阴影去掉，
    img 图片数组
    """
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if img[i,j,:].sum() > 3.5:
                img[i,j,:] = [1,1,1,1]
            elif img[i,j,3] < 0.1:
                img[i,j,:] = [0,0,0,0]
    return img
def dep_area(img):
    "return 分区feature"
    featurey = [False for i in range(img.shape[1])]
    for i in range(img.shape[1]):
        if img[1,i,1] == 0 and i > 10:
            featurey[i] = True
    featurex = [False for i in range(img.shape[0])]

    for i in range(img.shape[0]):
        if img[i,-1,1] == 0 and i < 40:
            featurex[i] = True
    return featurex,featurey

def deal_area1(img,featurex,featurey):
    """T求第一个True出现的索引"""
    indexx,indexy = 0,0
    for i in range(len(featurex)):
        if featurex[i] == False:
            indexx = i-1
            break
    for i in range(len(featurey)):
        if featurey[i] == True:
            indexy = i
            break
    #找出众数 mode1
    arr1 = img[0:indexx,indexy,0]
    mode1,count1 = mode(arr1)
    #找出需要的 rbgs  arrselect1
   
    for i in range(indexx):
        if img[i,indexy,0] == mode1:
            indexselect1 = i
            break
    arrselect1 = img[indexselect1,indexy,:]
    #转化为 arrselect1
    for i in range(indexx):
         for j in range(indexy,img.shape[1]):
             if  img[i,j,3] == 1:
                 img[i,j,:] = arrselect1                
    #大区域的 众数 mode2                    
    mode2,count2 = mode(img[-3,:,0])
    indexselect2 = 0
    #大区域要的 rgbs arrselect2
    for i in range(img.shape[1]):
        if img[-3,i,0] == mode2:
            indexselect2 = i
            break
    arrselect2 = img[-5,indexselect2,:]
    #把全部转化为arrselect2
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            #这个逻辑有点问题？？
            if img[i,j,3] == 1:
                if (i > indexx + 1) or (j < indexy - 1):
                    #print(img[i,j,:])
                    #为什么不能用这个？
                    #if img[i,j,:] != [1,1,1,1]:
                    # 用numpy的话
                    #不过总感觉 0 的 话兼容性不是很好
                    if np.sum(img[i,j,:]-[1,1,1,1]) !=0:
                    #if img[i,j,0] != 1 and img[1,j,1] !=1 and img[i,j,2] != 1:
                        #字旁边的阴影 用numpy
                        #两个相减
                        compa1 = img[i,j,:] - arrselect2
                        #print(compa1.max())
                        if np.max(compa1) < 0.2 and np.min(compa1) > -0.2:
                            
                            img[i,j,:] = arrselect2
    return img                  
#这样可以改变数组
#img[0,0,:] =[1,1,1,1]

#去除边框  feature1 判断去除的行  feature2 数  一开始方法为判断一个平面最大像素小于0.5  然而有些不适用 这个改为立体的
if __name__ == '__main__':

    parse = argparse.ArgumentParser()
    parse.add_argument('-p','--path',type=str,required=False,help='image path' )
    args = parse.parse_args()
    if args.path:
        PATH = args.path
    else:
        print('未指定-p参数，默认图片html.png')
    print('图片处理中...')
    img = np.array(mpimg.imread(PATH))

    feature1 = [True for i in range(img.shape[0])]
    for i in range(img.shape[0]):
        if img[i,:,:].max() < 0.5:
            feature1[i] = False
            
    feature2 = [True for i in range(img.shape[1])]
    for i in range(img.shape[1]):
        if img[:,i,:].max() < 0.5:
            feature2[i] = False

    imgg1 = img[feature1,:,:]
    imgg2 = imgg1[:,feature2,:]    

    imgg3 = write_transparent(imgg2.copy())
    #分组特征
    featurex,featurey = dep_area(imgg3)
    #用copy 这是引用传递
    imgg4 = deal_area1(imgg3.copy(),featurex,featurey)
    #保存图片
    mpimg.imsave('new_'+PATH,imgg4)
    print('图片处理成功！')
