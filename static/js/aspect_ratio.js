function gcd (a, b) {
    return (b == 0) ? a : gcd (b, a%b);
}
var w = screen.width;
var h = screen.height;
var r = gcd (w, h);
console.log("Aspect Ratio = ", w/r, ":", h/r);