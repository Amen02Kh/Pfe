function openTab(evt, tabName) {
    var i, formContent, tablinks;
    formContent = document.getElementsByClassName("form-content");
    for (i = 0; i < formContent.length; i++) {
        formContent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tab");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}
document.getElementById("defaultOpen").click();



$(document).ready(function(){
    $("#spam").click(function(){
      if($(this).is(":checked")){
        $("#email").show();
        $("#email").prop('required',true);
        $("#email").addClass('required-input');
      } else {
        $("#email").hide();
        $("#email").prop('required',false);
        $("#email").removeClass('required-input');
      }
    });
    
  
    $("#email").on('input', function() {
      if($(this).val() !== '') {
        $(this).removeClass('required-input');
      } else {
        $(this).addClass('required-input');
      }
    });
  });
  $(document).ready(function(){
    $("#scanner").click(function(){
      if($(this).is(":checked")){
        $("#domain").show();
        $("#domain").prop('required',true);
        $("#domain").addClass('required-input');
      } else {
        $("#domain").hide();
        $("#domain").prop('required',false);
        $("#domain").removeClass('required-input');
      }
    });
    
  
    $("#domain").on('input', function() {
      if($(this).val() !== '') {
        $(this).removeClass('required-input');
      } else {
        $(this).addClass('required-input');
      }
    });
  });