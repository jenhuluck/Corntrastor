'''
Created on Sep 18, 2019

@author: Anik
'''

from os import listdir
from os.path import isfile, join
from PIL import Image, ImageEnhance
from skimage.color import rgb2gray
from sklearn.cluster import KMeans
from skimage.io import imread
import colorsys, os, matplotlib.pyplot

INPUTFOLDERNAME = "raw_images"
INTERMEDFOLDERNAME = "processed_images"
OUTPUTFOLDERNAME = "filtered_images"


class Level(object):
    
    def __init__(self, minv, maxv, gamma):
        
        self.minv = minv / 255.0
        self.maxv = maxv / 255.0
        self._interval = self.maxv - self.minv
        self._invgamma = 1.0 / gamma

    def newLevel(self, value):
        
        if value <= self.minv: return 0.0
        if value >= self.maxv: return 1.0
        
        return ((value - self.minv) / self._interval) ** self._invgamma

    def convertAndLevel(self, band_values):
        
        h, s, v = colorsys.rgb_to_hsv(*(i / 255.0 for i in band_values))
        new_v = self.newLevel(v)
        return tuple(int(255 * i)
                for i
                in colorsys.hsv_to_rgb(h, s, new_v))
        

class File(object):
    
    def __init__(self, inF, outF):
        
        self.inF = inF
        self.outF = outF
    
    def getFilenames(self):
        
        if not os.path.isdir(self.inF):
            os.makedirs(self.inF)
            
        return [f for f in listdir(self.inF) if isfile(join(self.inF, f))]
    
    def getImages(self):
        
        filenames = self.getFilenames()
        imageList = []
        
        for file in filenames:
            imageList.append(self.openImg(self.inF + "/" + file))
        
        return imageList

    def getSKImages(self):
        
        filenames = self.getFilenames()
        imageList = []
        
        for file in filenames:
            imageList.append(self.openSKImg(self.inF + "/" + file))
        
        return imageList
    
    def setImages(self, imageList):
        
        if not os.path.isdir(self.outF):
            os.makedirs(self.outF)
        
        for i, img in enumerate(imageList):
            img.save(self.outF + "/{:03d}.png".format(i))
            
    def setSKImages(self, imageList):
        
        if not os.path.isdir(self.outF):
            os.makedirs(self.outF)
        
        for i, img in enumerate(imageList):
            matplotlib.pyplot.imsave((self.outF + "/{:03d}.png".format(i)), img, cmap='gray')
    
    def openImg(self, fileName):
        
        img = None
        
        try:
            img = Image.open(fileName)
        except FileNotFoundError:
            print ("Invalid filename")
        
        return img
    
    def openSKImg(self, fileName):
        
        img = None
        
        try:
            img = imread(fileName)
        except FileNotFoundError:
            print ("Invalid filename")
        
        return img
    
    
class Trim(object):
    
    def __init__(self, maxWhiteThresh, rowHeight):
        
        self.maxWhiteThresh = maxWhiteThresh
        self.rowHeight = rowHeight
    
    def naiveTrim(self, img, topTrim, bottomTrim):
    
        width, height = img.size
        
        left = 0
        right = width
        top = int(height * topTrim)
        bottom = int(height * bottomTrim)
        
        return img.crop((left, top, right, bottom))
    
    def smartTrim(self, img):
        
        width = img.size[0]
        
        left = 0
        right = width
        top = self.getTop(img)
        bottom = self.getBottom(img)
        
        return img.crop((left, top, right, bottom))
    
    def getTop(self, img):
        
        width, height = img.size
        
        left = 0
        right = width
        
        for i in range (int(height / (2 * self.rowHeight)) - 1):
            rowImg = img.crop((left, i * self.rowHeight, right, (i + 1) * self.rowHeight))
            pixels = rowImg.getdata()
            
            whiteThresh = 50
            count = 0
            
            for pixel in pixels:
                if pixel > whiteThresh:
                    count += 1
                    
            n = len(pixels)
            
            if (count / float(n)) < self.maxWhiteThresh:
                return ((i + 1) * self.rowHeight)
            
        return  (int(height / 2) - 1)
    
    def getBottom(self, img):
        
        width, height = img.size
        
        left = 0
        right = width
        
        for i in range (int(height / (2 * self.rowHeight)) - 1):
            rowImg = img.crop((left, height - ((i + 1) * self.rowHeight), right, height - (i * self.rowHeight)))
            pixels = rowImg.getdata()
            
            whiteThresh = 50
            count = 0
            
            for pixel in pixels:
                if pixel > whiteThresh:
                    count += 1
                    
            n = len(pixels)
            
            if (count / float(n)) < self.maxWhiteThresh:
                return (height - ((i + 1) * self.rowHeight))
            
        return  (int(height / 2) + 1)


def convertToRGB(img):
    
    img.load()
    
    rgb = Image.new("RGB", img.size, (255, 255, 255))
    rgb.paste(img, mask=img.split()[3])
    
    return rgb

    
def adjustLevel(img, minv=0, maxv=255, gamma=1.0):

    if img.mode != "RGB":
        raise ValueError("Image not in RGB mode")

    newImg = img.copy()

    leveller = Level(minv, maxv, gamma)
    levelled_data = [
        leveller.convertAndLevel(data)
        for data in img.getdata()]
    newImg.putdata(levelled_data)
    
    return newImg


def convertToGreyscale(img):
    
    return ImageEnhance.Contrast(img).enhance(50.0)


def binarizeImg(img):
    
    return img.convert('1')


def thresholdSegmentation(image):
    
    image = matplotlib.pyplot.imread('1117_607.png')
    image.shape
    
    # matplotlib.pyplot.imshow(image)
    
    gray = rgb2gray(image)
    # matplotlib.pyplot.imshow(gray, cmap='gray')
    
    gray_r = gray.reshape(gray.shape[0] * gray.shape[1])
    for i in range(gray_r.shape[0]):
        if gray_r[i] > gray_r.mean():
            gray_r[i] = 1
        else:
            gray_r[i] = 0
    gray = gray_r.reshape(gray.shape[0], gray.shape[1])
    # matplotlib.pyplot.imshow(gray, cmap='gray')
    
    # matplotlib.pyplot.imshow(image)
    
    gray = rgb2gray(image)
    gray_r = gray.reshape(gray.shape[0] * gray.shape[1])
    for i in range(gray_r.shape[0]):
        if gray_r[i] > gray_r.mean():
            gray_r[i] = 3
        elif gray_r[i] > 0.5:
            gray_r[i] = 2
        elif gray_r[i] > 0.25:
            gray_r[i] = 1
        else:
            gray_r[i] = 0
    gray = gray_r.reshape(gray.shape[0], gray.shape[1])
    matplotlib.pyplot.imsave('test.png', gray, cmap='gray')
    
    # img = Image.fromarray(gray , 'L')
    # return img


def kMeansSegmentation(image):
    
    pic = matplotlib.pyplot.imread('1117_607.png') / 225  # dividing by 255 to bring the pixel values between 0 and 1
    # print(pic.shape)
    # matplotlib.pyplot.imshow(pic)
    
    pic_n = pic.reshape(pic.shape[0] * pic.shape[1], pic.shape[2])
    pic_n.shape
    
    kmeans = KMeans(n_clusters=5, random_state=0).fit(pic_n)
    pic2show = kmeans.cluster_centers_[kmeans.labels_]
    
    cluster_pic = pic2show.reshape(pic.shape[0], pic.shape[1], pic.shape[2])
    # matplotlib.pyplot.imshow(cluster_pic)
    
    matplotlib.pyplot.imsave('test.png', cluster_pic)
    
    # img = Image.fromarray(cluster_pic , 'L')
    # return img

    
def filterClusters(image, thresh):
    
    # Initialize cluster count
    
    clusCount = 0
    row = len(image)
    col = len(image[0])
    
    for i in range(row):
        for j in range(col):
            
            if image[i][j] == 255:
                
                image[i][j] = 1
                
                # Initialize size of cluster as mutable object and set the minimum value to 1
                size = [1]
                # size.append(1)
                size[0] = 1 
                
                # Perform DFS (using Jen's DFS method)
                dfsWithSize(i, j, image, row, col, size)
                
                if size[0] > thresh:
                    image[i][j] = 255
                
                # Update cluster count
                clusCount += 1
    
    return image


def dfsWithSize(i, j, image, row, col, size):
    
    if(i < 0 or i >= row or j < 0 or j >= col):
        return
    
    if(image[i][j] == 0):
        return
    
    if(image[i][j] == 255):
        image[i][j] = 0
        size[0] += 1
    
    dfsWithSize(i + 1, j, image, row, col, size)
    dfsWithSize(i, j + 1, image, row, col, size)
    dfsWithSize(i - 1, j, image, row, col, size)
    dfsWithSize(i, j - 1, image, row, col, size)


def bulkProcess(imageList):
    
    processedImageList = []
    
    for i, img in enumerate(imageList):
        
        # newImg = kMeansSegmentation(img)
        
        # Convert image to RGB
        rgb = convertToRGB(img)
        
        # Adjust image level
        levelledImg = adjustLevel(rgb, 100, 255, 9.99)
        
        # Convert to greyscale
        grayImg = convertToGreyscale(levelledImg)
        
        # Binarize image
        binImg = binarizeImg(grayImg)
        
        # Initialize trimmer
        trimmer = Trim(0.1, 1)
        
        # Trim image (Naive)
        trimmedImg = trimmer.smartTrim(binImg)
        
        # Filter clusters by pixel density and dot representation
        # filteredImg = filterClusters(trimmedImg, 10)
        
        # Update processed image list
        processedImageList.append(trimmedImg)
        
        # Display status
        print("Image {:03d}.png processing completed".format(i))
    
    return processedImageList


def bulkFilter(imageList):
    
    filteredImageList = []
    
    for i, img in enumerate(imageList):
        
        # Filter clusters by pixel density and dot representation
        filteredImg = filterClusters(img, 10)
        
        # Update filtered image list
        filteredImageList.append(filteredImg)
        
        # Display status
        print("Image {:03d}.png cluster filtering completed".format(i))
        
    return filteredImageList


def main():
    
    # Initialize process handler
    handlerProcess = File(INPUTFOLDERNAME, INTERMEDFOLDERNAME)
    
    # Get images
    imageList = handlerProcess.getImages()
    
    # Process images
    processedImageList = bulkProcess(imageList)
    
    # Save images
    handlerProcess.setImages(processedImageList)
    
    # Initialize filter handler
    handlerFilter = File(INTERMEDFOLDERNAME, OUTPUTFOLDERNAME)
    
    # Get images
    imageList = handlerFilter.getSKImages()
    
    # Cluster filter images
    filteredImageList = bulkFilter(imageList)
    
    # Save images
    handlerFilter.setSKImages(filteredImageList)
    
    print("Program successfully terminated")
    return


if __name__ == '__main__':
    
    main()
    pass
