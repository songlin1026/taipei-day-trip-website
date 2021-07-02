// 創card函式
function createCard(data,whileNumber){
    // 創card中所有div
    let content=document.getElementById("content");
    let cardDiv=document.createElement("div");
    let photoDiv=document.createElement("div");
    let imgDiv=document.createElement("div");
    let nameDiv=document.createElement("div");
    let img = document.createElement("img");
    let describeImg=document.createElement("div");
    let mrtDiv=document.createElement("div");
    let categoryDiv=document.createElement("div");
    // 為新div設定class
    cardDiv.classList.add("card");
    photoDiv.classList.add("photo");
    imgDiv.classList.add("img");
    nameDiv.classList.add("name");            
    describeImg.classList.add("describe");
    mrtDiv.classList.add("mrt");
    categoryDiv.classList.add("category");
    // 設定超連結，滑鼠效果
    cardDiv.setAttribute("onclick", "location.href='/attraction/"+data.data[whileNumber].id+"'");
    cardDiv.setAttribute("onMouseOver","this.classList.add('cardMouse')")
    cardDiv.setAttribute("onMouseOut","this.classList.remove('cardMouse')")
    //抓取api資料
    let Name = document.createTextNode(data.data[whileNumber].name);
    let Category = document.createTextNode(data.data[whileNumber].category); 
    // 判斷MRT是否為null
    if(data.data[whileNumber].mrt==null){
        var Mrt= document.createTextNode("無法搭乘捷運到達");
    }else{
        var Mrt = document.createTextNode(data.data[whileNumber].mrt);
    };
    // 設定img參數
    img.setAttribute("src",data.data[whileNumber].images[0]);
    img.setAttribute("width","100%");
    img.setAttribute("height","158px");
    // 將div放入頁面
    nameDiv.appendChild(Name);
    mrtDiv.appendChild(Mrt);
    categoryDiv.appendChild(Category);
    content.appendChild(cardDiv);
    cardDiv.appendChild(photoDiv);
    photoDiv.appendChild(imgDiv);
    photoDiv.appendChild(nameDiv);
    imgDiv.appendChild(img);
    cardDiv.appendChild(describeImg);
    describeImg.appendChild(mrtDiv);
    describeImg.appendChild(categoryDiv);
};


function moreData(){
    if(scrolled==false){
        scrolled=true
        let reqmoreData=new XMLHttpRequest();
        let searchInput=document.getElementById("searchInput");
        // 判斷使用者是否使用搜尋
        if(searchInput.value==""){
            reqmoreData.open("get","/api/attractions?page="+page);
            reqmoreData.onload=function(){
                let data=JSON.parse(this.responseText);
                // 判斷是否有下一頁
                if(data.nextPage==null){
                    let whileNumber=0;
                    let loading_box=document.getElementById("loading_box")
                    loading_box.classList.add("display")
                    while (whileNumber<data.data.length){
                        createCard(data,whileNumber);
                        whileNumber+=1;
                    }
                }else{
                    page=data.nextPage;
                    var whileNumber=0;
                    while (whileNumber<12){
                        createCard(data,whileNumber);
                        whileNumber+=1;
                    };
                    scrolled=false 
                };
            };
        }else{
            // 搜尋關鍵字
            reqmoreData.open("get","/api/attractions?page="+page+"&keyword="+searchInput.value);
            reqmoreData.onload=function(){
                let data=JSON.parse(this.responseText);
                // 判斷是否還有下一頁
                if(data.nextPage==null & page==0){

                }else{
                    if(data.nextPage==null){
                        let whileNumber=0;
                        let loading_box=document.getElementById("loading_box")
                        loading_box.classList.add("display")
                        while (whileNumber<data.data.length){
                            createCard(data,whileNumber);
                            whileNumber+=1;
                        };
                    }else{
                        page=data.nextPage;
                        let whileNumber=0;
                        while (whileNumber<12){
                            createCard(data,whileNumber);
                            whileNumber+=1;
                        };
                        scrolled=false 
                    };
                }
            };          
        };    
        reqmoreData.send();
    };  
};

function searchData(){
    //刪除原有元素、設定page為0
    let content=document.getElementById("content");
    let card = document.getElementsByClassName("card");
    let carLength=card.length;
    let loading_box=document.getElementById("loading_box")
    loading_box.classList.remove("display")
    for(i=0;i<carLength;i++){
        content.removeChild(card[0]);
    };
    page=0;
    //抓取關鍵字
    let searchInput=document.getElementById("searchInput").value;
    let reqsearchData=new XMLHttpRequest();
    reqsearchData.open("get","/api/attractions?page="+page+"&keyword="+searchInput);
    reqsearchData.onload=function(){
        let data=JSON.parse(this.responseText);
        //判斷是否還有下一頁資料
        if(data.nextPage==null){
        let whileNumber=0;
        let loading_box=document.getElementById("loading_box")
        loading_box.classList.add("display")
            while (whileNumber<data.data.length){
                createCard(data,whileNumber);
                whileNumber+=1;
            };
        }else{
            page=data.nextPage;
            let whileNumber=0;
            while (whileNumber<12){
                createCard(data,whileNumber);
                whileNumber+=1;
            };
            scrolled=false 
        };
    };
    reqsearchData.send();
};