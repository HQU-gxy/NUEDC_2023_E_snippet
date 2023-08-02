#include <format>
#include <CLI/CLI.hpp>
#include <opencv2/videoio.hpp>
#include <spdlog/spdlog.h>
#include <opencv2/opencv.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>

std::string get_fourcc_name(int32_t fourcc){
  std::string s;
  s += static_cast<char>(fourcc & 0xFF);
  s += static_cast<char>((fourcc >> 8) & 0xFF);
  s += static_cast<char>((fourcc >> 16) & 0xFF);
  s += static_cast<char>((fourcc >> 24) & 0xFF);
  return s;
}

int main(){
  CLI::App app{"CV Example"};
  std::string device = "0";
  bool index = false;
  int width = 640;
  int height = 480;
  float fps = 30.0f;
  app.add_option("-d,--device", device, "Capture device. Could be index or filename");
  app.add_flag("-i,--index", index, "If OpenCV use `device` as index. If not, use `device` as filename");
  app.add_option("-w,--width", width, "Capture width");
  app.add_option("-h,--height", height, "Capture height");
  app.add_option("-f,--fps", fps, "Capture fps");
  CLI11_PARSE(app);

  spdlog::info("OpenCV version: {}", CV_VERSION);

  cv::VideoCapture cap;
  if (index){
    int idx;
    auto [p, ec] = std::from_chars(device.data(), device.data() + device.size(), idx);
    assert(ec == std::errc{});
    cap = cv::VideoCapture(idx);
    spdlog::info("VideoCapture use {} as index", idx);
  } else {
    cap = cv::VideoCapture(device);
    spdlog::info("VideoCapture use {} as filename", device);
  }
  cap.set(cv::CAP_PROP_FRAME_WIDTH, width);
  cap.set(cv::CAP_PROP_FRAME_HEIGHT, height);
  cap.set(cv::CAP_PROP_FPS, fps);
  auto fourcc = cv::VideoWriter::fourcc('Y', 'U', 'Y', 'V');
  cap.set(cv::CAP_PROP_FOURCC, fourcc);
  spdlog::info("Set capture width: {}, height: {}, fps: {}, fourcc: {}({})", width, height, fps, fourcc, get_fourcc_name(fourcc));
  auto w = cap.get(cv::CAP_PROP_FRAME_WIDTH);
  auto h = cap.get(cv::CAP_PROP_FRAME_HEIGHT);
  auto f = cap.get(cv::CAP_PROP_FPS);
  auto cc = cap.get(cv::CAP_PROP_FOURCC);
  auto cc_s = get_fourcc_name(cc);
  spdlog::info("Get Capture width: {}, height: {}, fps: {}, fourcc: {}({})", w, h, f, cc, cc_s);

  while(cap.isOpened()){
    cv::Mat frame;
    cap >> frame;
    if (frame.empty()){
      spdlog::info("Frame is empty");
      break;
    }
    cv::imshow("frame", frame);
    if (cv::waitKey(1) == 'q'){
      break;
    }
  }

  return 0;
}
