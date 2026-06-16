import matplotlib.pyplot as plt
from skimage.filters import threshold_otsu, threshold_yen
import tifffile

def plotGraph(data1, data2, data3, titles, colors):       
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    axes[0].imshow(data1, cmap=colors[0])
    axes[0].set_title(titles[0])
    axes[1].imshow(data2, cmap=colors[1])
    axes[1].set_title(titles[1])
    if len(colors) ==3 :
        axes[2].imshow(data3, cmap=colors[2])
    else:
        axes[2].imshow(data3)
    axes[2].set_title(titles[2])
    plt.tight_layout()
    plt.show()

def readTiffImage(path, logger):
    try:
        img = tifffile.imread(path)
    except FileNotFoundError:
        logger.error(f"Image file not found: {path}")
        raise
    except Exception as e:
        logger.error(f"Error loading image: {e}")
        raise
    return img

def writeTifImage(filename, img):
     tifffile.imwrite(filename, img)

def detect_fixed_threshold(ch_smooth, threshold_value):
    return ch_smooth > threshold_value

def detect_otsu(ch_smooth, nbins):
    """Otsu's method"""
    return ch_smooth > threshold_otsu(ch_smooth, nbins=nbins)

def detect_yen(ch_smooth):
    """Yen's method"""
    return ch_smooth > threshold_yen(ch_smooth)