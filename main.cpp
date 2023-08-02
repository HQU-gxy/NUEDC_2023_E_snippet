#include <CLI/CLI.hpp>
#include <cstdint>
#include <format>
#include <opencv2/opencv.hpp>
#include <ratio>
#include <spdlog/spdlog.h>

std::string get_fourcc_name(int32_t fourcc) {
  std::string s;
  s += static_cast<char>(fourcc & 0xFF);
  s += static_cast<char>((fourcc >> 8) & 0xFF);
  s += static_cast<char>((fourcc >> 16) & 0xFF);
  s += static_cast<char>((fourcc >> 24) & 0xFF);
  return s;
}

int main() {
  CLI::App app{"CV Example"};
  std::string device = "0";
  bool no_index = false;
  int width = 640;
  int height = 480;
  float fps = 30.0f;
  app.add_option("-d,--device", device,
                 "Capture device. Could be index or filename");
  app.add_flag(
      "--no-index", no_index,
      "If OpenCV use `device` as index. If true, use `device` as filename");
  app.add_option("--width", width, "Capture width");
  app.add_option("--height", height, "Capture height");
  app.add_option("--fps", fps, "Capture fps");
  CLI11_PARSE(app);

  spdlog::info("OpenCV version: {}", CV_VERSION);

  // openCV use GStreamer as backend by default
  cv::VideoCapture cap;
  if (!no_index) {
    int idx;
    auto [p, ec] =
        std::from_chars(device.data(), device.data() + device.size(), idx);
    if (ec != std::errc()) {
      spdlog::error("Cannot parse device as index: {}", device);
      return 1;
    }
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
  spdlog::info(
      "Set capture width: {}, height: {}, fps: {}, fourcc: {:#02x}({})", width,
      height, fps, fourcc, get_fourcc_name(fourcc));
  auto w = cap.get(cv::CAP_PROP_FRAME_WIDTH);
  auto h = cap.get(cv::CAP_PROP_FRAME_HEIGHT);
  auto f = cap.get(cv::CAP_PROP_FPS);
  auto cc = static_cast<uint32_t>(cap.get(cv::CAP_PROP_FOURCC));
  auto cc_s = get_fourcc_name(cc);
  spdlog::info(
      "Get Capture width: {}, height: {}, fps: {}, fourcc: {:#02x}({})", w, h,
      f, cc, cc_s);
  constexpr auto average_interval = 100;

  using dur = std::chrono::high_resolution_clock::duration;

  auto average_frametime = dur::zero();
  size_t frame_count = 0;
  size_t total_frame_count = 0;
  auto start_time = std::chrono::high_resolution_clock::now();
  while (cap.isOpened()) {
    cv::Mat frame;
    cap >> frame;
    if (frame.empty()) {
      spdlog::info("Frame is empty");
      break;
    }
    auto now = std::chrono::high_resolution_clock::now();
    frame_count++;
    total_frame_count++;
    // calculate average frametime every 100 frames
    // https://stackoverflow.com/questions/52068277/change-frame-rate-in-opencv-3-4-2
    if (frame_count % average_interval == 0) {
      auto diff = now - start_time;
      average_frametime = diff / frame_count;
      start_time = now;
      frame_count = 0;
      spdlog::info(
          "Average frametime: {:.2}ms@{}",
          std::chrono::duration_cast<std::chrono::duration<double, std::milli>>(
              average_frametime)
              .count(),
          total_frame_count);
    }
    // for some reason high gui is broken on my machine (Windows 11)
    // so imshow won't work
    // cv::imshow("frame", frame);
  }

  return 0;
}
