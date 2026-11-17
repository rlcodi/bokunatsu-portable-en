import AppKit
import CoreText
let args = CommandLine.arguments
let size = CGFloat(Double(args[1])!), baseline = CGFloat(Double(args[2])!)
let chars = Array(args[3].unicodeScalars)
var font: CTFont
if args.count > 4 {
    let url = URL(fileURLWithPath: args[4]) as CFURL
    let descs = CTFontManagerCreateFontDescriptorsFromURL(url) as! [CTFontDescriptor]
    font = CTFontCreateWithFontDescriptor(descs[0], size, nil)
} else {
    var desc = NSFont.systemFont(ofSize: size, weight: .medium).fontDescriptor
    if let r = desc.withDesign(.rounded) { desc = r }
    font = NSFont(descriptor: desc, size: size)! as CTFont
}
let cs = CGColorSpaceCreateDeviceGray()
for u in chars {
    var buf = [UInt8](repeating: 0, count: 32 * 16)
    let ctx = CGContext(data: &buf, width: 32, height: 16, bitsPerComponent: 8, bytesPerRow: 32, space: cs, bitmapInfo: CGImageAlphaInfo.none.rawValue)!
    ctx.setFillColor(gray: 1, alpha: 1)
    let s = NSAttributedString(string: String(Character(u)), attributes: [NSAttributedString.Key(kCTFontAttributeName as String): font, .foregroundColor: NSColor.white])
    let line = CTLineCreateWithAttributedString(s)
    let adv = CTLineGetTypographicBounds(line, nil, nil, nil)
    ctx.textPosition = CGPoint(x: 1, y: baseline)
    CTLineDraw(line, ctx)
    print(u.value, String(format: "%.2f", adv), buf.map { String(format: "%02x", $0) }.joined())
}
