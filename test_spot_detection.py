from spot_detection import SpotDetection

## TODO: configure pytest

# Test 1 spot detection
types = ["DAPI", "GFP"]
determinant = 0

path = "data/sample_image.tif"
detector = SpotDetection(path, types, det=0)
detector.run()
print(detector.results[types[0]]["n_spots_ch"] == 9)
print(detector.results[types[1]]["n_spots_ch"] == 260)

# # Test 2: non configured type
#types = ["DAPI", "NEW"]
#detector = SpotDetection(path, types, det=0)
##detector.run()

# Test 3: Non tif image
#path = "data/sample_image.jpg"
#detector = SpotDetection(path, types, det=0)
#detector.run()

# Test 4: ...
