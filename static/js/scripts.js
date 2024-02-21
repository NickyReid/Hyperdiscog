    function loadingButton(btn_id, url=null, loading_msg=null) {
       btn = document.getElementById(btn_id);
       if (loading_msg != null){
        btn.innerHTML = loading_msg;
       };
       btn.disabled = true;
       if (url != null){
        window.open(url,"_self")
       };
     };

    function formLoadingButton(btn_id, form_id, field_id, loading_msg="Please wait...") {
       field = document.getElementById(field_id);
       btn = document.getElementById(btn_id);
       if (field.value != ""){
           btn.value = loading_msg;
           btn.disabled = true;
           return true;
       }
       else{
         return false;
       };
     };

    var showInfoText = false;

    function toggleInfoDisplay(){
        showInfoText = !showInfoText;
        var whatIs = document.getElementById("what-is-lasthop");
        var infoText = document.getElementById("info-text");
        if (showInfoText == true){
            infoText.style.display = "block";
            whatIs.style.display = "none";
        } else {
            infoText.style.display = "none";
            whatIs.style.display = "block";
        }
    };

    function toggleAlbumTypeSelected(albumType){
        var albumTypeList = document.getElementById(albumType +"-list");
        if (albumTypeList.style.display == "block"){
        albumTypeList.style.display = "none";
        }
        else {
         albumTypeList.style.display = "block";
        }
    };

    var removeDuplicates = true;

    function toggleRemoveDuplicates(){
        var removeDuplicatesOptions = document.getElementById("remove-duplicates-options");
        removeDuplicates = !removeDuplicates;
        if (removeDuplicates == true){
            removeDuplicatesOptions.style.display = "block";
        } else {
            removeDuplicatesOptions.style.display = "none";
        }
    };
