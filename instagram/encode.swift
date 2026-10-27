// encode.swift FRAMES_DIR OUT.mp4 FPS — збирає PNG-кадри (f00000.png…) у H.264 MP4
import AVFoundation
import AppKit
let a = CommandLine.arguments
let dir = URL(fileURLWithPath: a[1]), out = URL(fileURLWithPath: a[2]), fps = Int32(a[3])!
let files = try FileManager.default.contentsOfDirectory(atPath: dir.path).filter { $0.hasSuffix(".png") }.sorted()
let first = NSImage(contentsOf: dir.appendingPathComponent(files[0]))!
let w = Int(first.representations[0].pixelsWide), h = Int(first.representations[0].pixelsHigh)
try? FileManager.default.removeItem(at: out)
let writer = try AVAssetWriter(outputURL: out, fileType: .mp4)
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
  AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: w, AVVideoHeightKey: h,
  AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 8_000_000, AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel]])
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
  kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB, kCVPixelBufferWidthKey as String: w, kCVPixelBufferHeightKey as String: h])
writer.add(input); writer.startWriting(); writer.startSession(atSourceTime: .zero)
for (i, f) in files.enumerated() {
  let img = NSImage(contentsOf: dir.appendingPathComponent(f))!
  var rect = CGRect(x: 0, y: 0, width: w, height: h)
  let cg = img.cgImage(forProposedRect: &rect, context: nil, hints: nil)!
  var pb: CVPixelBuffer?
  CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &pb)
  CVPixelBufferLockBaseAddress(pb!, [])
  let ctx = CGContext(data: CVPixelBufferGetBaseAddress(pb!), width: w, height: h, bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(pb!), space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
  ctx.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))
  CVPixelBufferUnlockBaseAddress(pb!, [])
  while !input.isReadyForMoreMediaData { usleep(2000) }
  adaptor.append(pb!, withPresentationTime: CMTime(value: CMTimeValue(i), timescale: fps))
}
input.markAsFinished()
let sem = DispatchSemaphore(value: 0)
writer.finishWriting { sem.signal() }
sem.wait()
print("ok \(files.count) frames → \(out.lastPathComponent)", writer.status == .completed ? "" : "ERROR \(String(describing: writer.error))")
