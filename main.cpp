#include <CLI/CLI.hpp>
#include <concepts>
#include <cstdint>
#include <format>
#include <opencv2/core/matx.hpp>
#include <opencv2/core/types.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/opencv.hpp>
#include <optional>
#include <ranges>
#include <ratio>
#include <span>
#include <spdlog/spdlog.h>
#include <vector>

constexpr auto MAX_TAIL_SIZE = 10;
constexpr auto MAX_TAIL_THICKNESS = 4;

namespace utils {
struct Color {
  uint8_t r;
  uint8_t g;
  uint8_t b;

  Color(uint8_t r, uint8_t g, uint8_t b) : r(r), g(g), b(b) {}
  Color(uint32_t rgb) {
    r = (rgb >> 16) & 0xff;
    g = (rgb >> 8) & 0xff;
    b = rgb & 0xff;
  }

  /**
   * @brief convert to uint32_t
   * @return implicit conversion. operator overloading.
   */
  operator uint32_t() const { return (r << 16) | (g << 8) | b; }

  cv::Vec3f toBGR() const { return cv::Vec3f(b, g, r); }
};
namespace Colors {
const auto Red = Color(0xff0000);
const auto Green = Color(0x00ff00);
const auto Blue = Color(0x0000ff);
const auto White = Color(0xffffff);
const auto Cyan = Color(0x00ffff);
const auto Magenta = Color(0xff00ff);
const auto Yellow = Color(0xffff00);
const auto Amber = Color(0xffbf00);
const auto Orange = Color(0xff8000);
const auto Purple = Color(0x8000ff);
const auto Pink = Color(0xff0080);
const auto Azure = Color(0x0080ff);
}; // namespace Colors

// - https://www.reedbeta.com/blog/ranges-compatible-containers/
// - https://en.cppreference.com/w/cpp/ranges/slide_view
//
// a view whose `M` th element is a view over the `M` th through `(M + N - 1)`
// th elements of another view
template <std::ranges::viewable_range R>
constexpr std::ranges::view auto slide_view(R &&r, size_t sz) {
  return std::views::iota(0u, std::ranges::distance(r) - sz + 1) |
         std::views::transform([&, i = 0u](auto) mutable {
           return std::span(&*std::ranges::begin(r) + i++, sz);
         });
}
}; // namespace utils

std::string get_fourcc_name(int32_t fourcc) {
  std::string s;
  s += static_cast<char>(fourcc & 0xFF);
  s += static_cast<char>((fourcc >> 8) & 0xFF);
  s += static_cast<char>((fourcc >> 16) & 0xFF);
  s += static_cast<char>((fourcc >> 24) & 0xFF);
  return s;
}

auto detect_circles(cv::Mat &img) -> std::vector<cv::Vec3f> {
  std::vector<cv::Vec3f> ret;
  // https://docs.opencv.org/3.4/d6/d50/classcv_1_1Size__.html
  // height first
  const auto [h, w] = img.size();
  cv::HoughCircles(img, ret, cv::HOUGH_GRADIENT, 2, h * 2, 300, 0.9, 5, 10);
  return ret;
}

void draw_circles(
    cv::Mat &img, const std::vector<cv::Vec3f> &circles,
    std::optional<std::vector<cv::Point>> last_state = std::nullopt) {
  using namespace utils;
  const auto red = Colors::Red.toBGR();
  for (const auto &c : circles) {
    const auto x = c[0];
    const auto y = c[1];
    const auto r = c[2];
    const auto center = cv::Point(x, y);
    const auto radius = r;
    cv::circle(img, center, radius, red, 2);
    if (last_state.has_value()) {
      // might be expensive
      last_state.value().insert(last_state.value().begin(), center);
      if (last_state.value().size() > MAX_TAIL_SIZE) {
        last_state.value().pop_back();
      }
    }
  }
  if (last_state.has_value()) {
    auto thickness = MAX_TAIL_THICKNESS;
    size_t i = 0;
    const auto window_sz = 2;
    auto slide = utils::slide_view(std::span(last_state.value()), window_sz);
    // https://en.cppreference.com/w/cpp/ranges/slide_view
    // https://medium.com/@simontoth/daily-bit-e-of-c-std-views-adjacent-std-views-pairwise-809363044218
    for (const auto ps : slide) {
      thickness = static_cast<int>(
          std::sqrt(MAX_TAIL_THICKNESS / static_cast<float>(i + 1)) * 2.5);
      cv::line(img, ps[0], ps[1], red, thickness);
      i += 1;
    }
  }
}

/**
 * @brief
 *
 * @param in    input image. won't be modified
 * @param out   output image.
 * @param lower color in LAB color space three dimension
 * @param upper color in LAB color space three dimension
 */
void handle_image_color_range(const cv::Mat &in, cv::Mat &out,
                              const cv::Scalar &lower,
                              const cv::Scalar &upper) {
  cv::GaussianBlur(in, out, cv::Size(5, 5), 2, 2);
  cv::cvtColor(out, out, cv::COLOR_BGR2Lab);
  cv::inRange(out, lower, upper, out);
  cv::GaussianBlur(out, out, cv::Size(5, 5), 2, 2);
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
  const auto w = cap.get(cv::CAP_PROP_FRAME_WIDTH);
  const auto h = cap.get(cv::CAP_PROP_FRAME_HEIGHT);
  const auto f = cap.get(cv::CAP_PROP_FPS);
  const auto cc = static_cast<uint32_t>(cap.get(cv::CAP_PROP_FOURCC));
  const auto cc_s = get_fourcc_name(cc);
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
