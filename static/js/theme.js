"use strict";

const mainImg = document.getElementById("img-main");
const btnMain = document.getElementById("theme-toggle");

btnMain.addEventListener("click", () => {
  document.body.classList.toggle("dark-theme");
  mainImg.setAttribute("src", document.body.classList.contains("dark-theme") ? darkThemeImageUrl : lightThemeImageUrl);
});
