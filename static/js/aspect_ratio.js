function gcd (a, b) {
    return (b == 0) ? a : gcd (b, a%b);
}
var w = window.innerWidth;
var h = window.innerHeight;
var r = gcd (w, h);
console.log("Aspect Ratio = ", w/r, ":", h/r);

if (w/r < h/r) {
    alert("Warning! Website may be unusable in portrait mode.");
}