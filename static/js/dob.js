<<<<<<< HEAD
$('.validate').mask("99/99/9999");
$('.validate').change(function(){

if($(this).val().substring(0,2) > 12 || $(this).val().substring(0,2) == "00") {
alert("Iregular Month Format");
return false;
}
if($(this).val().substring(3,5) > 31 || $(this).val().substring(0,2) == "00") {
alert("Iregular Date Format");
return false;
}
=======
$('.validate').mask("99/99/9999");
$('.validate').change(function(){

if($(this).val().substring(0,2) > 12 || $(this).val().substring(0,2) == "00") {
alert("Iregular Month Format");
return false;
}
if($(this).val().substring(3,5) > 31 || $(this).val().substring(0,2) == "00") {
alert("Iregular Date Format");
return false;
}
>>>>>>> f0664b25e0e2c0621c944bed919f34efc1cc8918
 });