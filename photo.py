# coding:utf-8
# Precondition: install image, pytesseract, tesseract, qhull
# sudo apt-get install tesseract-ocr-eng tesseract-ocr-chi-sim
try:
	import Image,ImageEnhance,ImageFilter, ImageDraw 
except ImportError:
	from PIL import Image
	from wand.image import Image

import pytesseract
import tesseract
import string
import simplejson

# ID card under recognition
image_name="ID3.jpg"

# 二值化 
threshold = 140
table = [] 

for i in range(256): 

	if i < threshold: 

		table.append(0) 

	else: 

		table.append(1) 

#二值判断,如果确认是噪声,用改点的上面一个点的灰度进行替换  
#该函数也可以改成RGB判断的,具体看需求如何  
def getPixel(image,x,y,G,N):  
	L = image.getpixel((x,y))  
	if L > G:  
		L = True  
	else:  
		L = False  
  
	nearDots = 0  
	if L == (image.getpixel((x - 1,y - 1)) > G):  
		nearDots += 1  
	if L == (image.getpixel((x - 1,y)) > G):  
		nearDots += 1  
	if L == (image.getpixel((x - 1,y + 1)) > G):  
		nearDots += 1  
	if L == (image.getpixel((x,y - 1)) > G):  
		nearDots += 1  
	if L == (image.getpixel((x,y + 1)) > G):  
		nearDots += 1  
	if L == (image.getpixel((x + 1,y - 1)) > G):  
		nearDots += 1  
	if L == (image.getpixel((x + 1,y)) > G):  
		nearDots += 1  
	if L == (image.getpixel((x + 1,y + 1)) > G):  
		nearDots += 1  
  
	if nearDots < N:  
		return image.getpixel((x,y-1))  
	else:  
		return None  

# 降噪   
# 根据一个点A的RGB值，与周围的8个点的RBG值比较，设定一个值N（0 <N <8），
# 	当A的RGB值与周围8个点的RGB相等数小于N时，此点为噪点   
# G: Integer 图像二值化阀值   
# N: Integer 降噪率 0 <N <8   
# Z: Integer 降噪次数   
# 输出   
#  0：降噪成功   
#  1：降噪失败 
def filterNoise(image,G,N,Z):  
	draw = ImageDraw.Draw(image)  
  
	for i in xrange(0,Z):  
		for x in xrange(1,image.size[0] - 1):  
			for y in xrange(1,image.size[1] - 1):  
				color = getPixel(image,x,y,G,N)  
				if color != None:  
					draw.point((x,y),color)  


def string_process(original_str):
	dict = {
		'name':'',
		'gender':'',
		'nationality':'',
		'id_no':''
	};


	splict_str = original_str.split('\n') 
	line_count = 0

	for line in splict_str:
		ns_str = line.replace(" ", "")
		if (ns_str == ""):
			continue
		line_count +=1


		# ---Name---
		if (line_count == 1): 
			name = line[-9:] #Current names with inner space if twi-charactors

			dict['name'] = name.replace(" ", "")


		# ---Gender & Nationality ---
		if (line_count == 2): 
			#temp = line.decode(encoding='UTF-8', errors='strict')
			line = line.replace(" ", "")
			gender_position = line.find('男')
			if gender_position == -1: # Not find 'male'
				gender_position = line.find('女')
			
			if gender_position == -1: # Not find 'Female'
				print "This line cannot be recognized."
			else:
				dict['gender'] = line[gender_position:gender_position+3]
				dict['nationality'] = line[gender_position+9:]


		# ---ID Number---
		id_no_position = gender_position = line.find("公民身份号码") 
		if (id_no_position == -1):
			# Other useless lines
			print "------>"
		else:
			line = line.replace(" ", "")
			dict['id_no'] = line[id_no_position+18:]

	return dict

def main():
	Im = Image.open(image_name)
	print Im.mode,Im.size,Im.format

	# 1.GrayScale
	Im = Image.open(image_name).convert('L')	#Convert to grayscale
	Im.save('g_'+image_name) 

	# 2. Filter noise 
	#filterNoise(Im,70,2,4)		#slightly [1] //Prefered Value: G = 50,N = 4,Z = 4 
	#Im = Im.filter(ImageFilter.MedianFilter())	#//Dis: Slow

	Im = Im.point(table,'1')	#strongly //Ad: Fast Dis: Over Filter
	Im.save('b_'+image_name) 

	# 3. Enhance contrast
	enhancer = ImageEnhance.Contrast(Im)	#Comment this while use Strongly Filter
	#Im = enhancer.enhance(1.5)	#slightly [2]
	#Im.save('En_'+image_name) 

	# 4. 倾斜矫正技术。
	
	# Output
	Im.save('Treated.jpg')

	text = pytesseract.image_to_string(Im,'chi_sim')
	print text
	print "_________________Original Text___________________"

	processed_string = string_process(text)
	print simplejson.dumps(processed_string, encoding="UTF-8", ensure_ascii=False)
	print "_________________Processed Text___________________"



if __name__ == '__main__':  
	main()  