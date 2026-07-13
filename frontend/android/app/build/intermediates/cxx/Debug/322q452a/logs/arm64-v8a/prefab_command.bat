@echo off
"C:\\Program Files\\Java\\jdk-17\\bin\\java" ^
  --class-path ^
  "C:\\Users\\vishn\\.gradle\\caches\\modules-2\\files-2.1\\com.google.prefab\\cli\\2.1.0\\aa32fec809c44fa531f01dcfb739b5b3304d3050\\cli-2.1.0-all.jar" ^
  com.google.prefab.cli.AppKt ^
  --build-system ^
  cmake ^
  --platform ^
  android ^
  --abi ^
  arm64-v8a ^
  --os-version ^
  24 ^
  --stl ^
  c++_shared ^
  --ndk-version ^
  27 ^
  --output ^
  "C:\\Users\\vishn\\AppData\\Local\\Temp\\agp-prefab-staging4786095652570725869\\staged-cli-output" ^
  "C:\\Users\\vishn\\Documents\\smart-civic\\frontend\\android\\app\\build\\intermediates\\cxx\\refs\\react-native-reanimated\\4j3z6i5i" ^
  "C:\\Users\\vishn\\Documents\\smart-civic\\frontend\\android\\app\\build\\intermediates\\cxx\\refs\\react-native-worklets\\3y3f6333" ^
  "C:\\Users\\vishn\\.gradle\\caches\\9.3.1\\transforms\\2b7c23aa4547eb79508e5d3aa3f2bc7a\\workspace\\transformed\\react-android-0.86.0-debug\\prefab" ^
  "C:\\Users\\vishn\\.gradle\\caches\\9.3.1\\transforms\\09e67ac42fe00929cdf7c316b1464038\\workspace\\transformed\\hermes-android-250829098.0.14-debug\\prefab" ^
  "C:\\Users\\vishn\\.gradle\\caches\\9.3.1\\transforms\\3c01aea05d2737e987399f1309ae090e\\workspace\\transformed\\fbjni-0.7.0\\prefab"
