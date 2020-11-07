// https://www.w3schools.com/howto/howto_js_sidenav.asp
function openNav() {
    document.getElementById("sideMenu").style.width = "15%";
    document.getElementById("rightMain").style.marginLeft = "15%";
    // if (!location.pathname.includes("index.html")) {
    //     document.body.style.backgroundColor = "rgba(0,0,0,0.4)";
    // }
    // document.getElementById("menuButton").style.visibility = "hidden";
    }

function closeNav() {
    document.getElementById("sideMenu").style.width = "0";
    document.getElementById("rightMain").style.marginLeft = "0";
    // if (!location.pathname.includes("index.html")) {
    //     document.body.style.backgroundColor = "white";
    // }
    // document.getElementById("menuButton").style.visibility = "visible";
}

function toggleNav(){
    if (document.getElementById("sideMenu").style.width == "0px") {
        openNav();
    } else {
        closeNav();
    }
}