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
 });