// rtext <ttf> <size> <W> <H> <stroke> <xscale> <out.bin> <text>   (text lines separated by \n, centred in WxH; line gap via env LG)
// writes W*H fill coverage then W*H stroke(+fill) coverage, 8-bit, top row first
import AppKit
import CoreText
let a = CommandLine.arguments
let size = CGFloat(Double(a[2])!), W = Int(a[3])!, H = Int(a[4])!, stroke = CGFloat(Double(a[5])!), xs = CGFloat(Double(a[6])!)
let lines = a[8].replacingOccurrences(of: "\\n", with: "\n").components(separatedBy: "\n")
let descs = CTFontManagerCreateFontDescriptorsFromURL(URL(fileURLWithPath: a[1]) as CFURL) as! [CTFontDescriptor]
let font = CTFontCreateWithFontDescriptor(descs[0], size, nil)
let lg = CGFloat(Double(ProcessInfo.processInfo.environment["LG"] ?? "0") ?? 0)
let track = CGFloat(Double(ProcessInfo.processInfo.environment["TRACK"] ?? "0") ?? 0)
let dy = CGFloat(Double(ProcessInfo.processInfo.environment["DY"] ?? "0") ?? 0)
let align = ProcessInfo.processInfo.environment["ALIGN"] ?? "center"
let valign = ProcessInfo.processInfo.environment["VALIGN"] ?? "center"
if ProcessInfo.processInfo.environment["MEASURE"] != nil {
    for t in lines {
        let s = NSAttributedString(string: t, attributes: [NSAttributedString.Key(kCTFontAttributeName as String): font, .kern: track])
        print(String(format: "%.2f", Double(CTLineGetTypographicBounds(CTLineCreateWithAttributedString(s), nil, nil, nil)) * Double(xs)))
    }
    exit(0)
}
let cs = CGColorSpaceCreateDeviceGray()
let asc = CTFontGetCapHeight(font), lineH = size + lg
let total = CGFloat(lines.count - 1) * lineH + asc
func pass(_ mode: Int) -> [UInt8] {
    var buf = [UInt8](repeating: 0, count: W * H)
    let ctx = CGContext(data: &buf, width: W, height: H, bitsPerComponent: 8, bytesPerRow: W, space: cs, bitmapInfo: CGImageAlphaInfo.none.rawValue)!
    ctx.setFillColor(gray: 1, alpha: 1); ctx.setStrokeColor(gray: 1, alpha: 1)
    ctx.setLineJoin(.round); ctx.setLineWidth(stroke * 2)
    for (i, t) in lines.enumerated() {
        let s = NSAttributedString(string: t, attributes: [NSAttributedString.Key(kCTFontAttributeName as String): font, .foregroundColor: NSColor.white, .kern: track])
        let line = CTLineCreateWithAttributedString(s)
        let w = CGFloat(CTLineGetTypographicBounds(line, nil, nil, nil)) * xs
        let top = (valign == "top" ? 1 : (CGFloat(H) - total) / 2) + CGFloat(i) * lineH
        let base = CGFloat(H) - top - asc + dy
        ctx.saveGState()
        ctx.translateBy(x: align == "left" ? 1 : (align == "right" ? CGFloat(W) - w - 1 : (CGFloat(W) - w) / 2), y: base); ctx.scaleBy(x: xs, y: 1)
        ctx.textPosition = .zero
        ctx.setTextDrawingMode(mode == 0 ? .fill : .fillStroke)
        CTLineDraw(line, ctx)
        ctx.restoreGState()
    }
    return buf
}
var out = pass(0)
out += stroke > 0 ? pass(1) : out
FileManager.default.createFile(atPath: a[7], contents: Data(out))
