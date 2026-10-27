// probe.swift VIDEO OUTDIR N — друкує параметри відео й зберігає N кадрів-превʼю (з урахуванням повороту)
import AVFoundation
import AppKit

let a = CommandLine.arguments
let url = URL(fileURLWithPath: a[1]), out = URL(fileURLWithPath: a[2]), n = Int(a[3]) ?? 6
let asset = AVURLAsset(url: url)
let sem = DispatchSemaphore(value: 0)
Task {
  let dur = try await asset.load(.duration).seconds
  let v = try await asset.loadTracks(withMediaType: .video).first!
  let size = try await v.load(.naturalSize), tf = try await v.load(.preferredTransform), fps = try await v.load(.nominalFrameRate)
  let r = CGRect(origin: .zero, size: size).applying(tf)
  let hasAudio = !(try await asset.loadTracks(withMediaType: .audio)).isEmpty
  print(String(format: "%@ dur=%.2fs natural=%.0fx%.0f display=%.0fx%.0f fps=%.1f audio=%@", url.lastPathComponent, dur, size.width, size.height, abs(r.width), abs(r.height), fps, hasAudio ? "yes" : "no"))
  let gen = AVAssetImageGenerator(asset: asset)
  gen.appliesPreferredTrackTransform = true
  gen.maximumSize = CGSize(width: 360, height: 640)
  gen.requestedTimeToleranceBefore = .zero; gen.requestedTimeToleranceAfter = .zero
  for i in 0..<n {
    let t = dur * (Double(i) + 0.5) / Double(n)
    let (img, _) = try await gen.image(at: CMTime(seconds: t, preferredTimescale: 600))
    let rep = NSBitmapImageRep(cgImage: img)
    let name = url.deletingPathExtension().lastPathComponent + String(format: "_%02d_%05.1fs.jpg", i, t)
    try rep.representation(using: .jpeg, properties: [.compressionFactor: 0.7])!.write(to: out.appendingPathComponent(name))
  }
  sem.signal()
}
sem.wait()
