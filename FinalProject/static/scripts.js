// https://www.w3schools.com/howto/howto_js_sidenav.asp
function openNav() {
    document.getElementById("sideMenu").style.width = "15%";
    document.getElementById("rightMain").style.marginLeft = "15%";
    }

function closeNav() {
    document.getElementById("sideMenu").style.width = "0";
    document.getElementById("rightMain").style.marginLeft = "0";
}

function toggleNav(){
    if (document.getElementById("sideMenu").style.width == "0px") {
        openNav();
    } else {
        closeNav();
    }
}