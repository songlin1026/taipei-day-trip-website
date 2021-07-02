    //選擇時間
    function changeLeftTime(){
        let changeLeftTime=document.getElementById("changeLeftTime")
        let changeRightTime=document.getElementById("changeRightTime")
        time="morning"
        changeLeftTime.classList.add("changeTime")
        changeRightTime.classList.remove("changeTime")
        let moneyContent=document.getElementById("moneyContent")
        let dollor="2000"
        moneyContent.textContent=dollor
    }
    function changeRightTime(){
        let changeLeftTime=document.getElementById("changeLeftTime")
        let changeRightTime=document.getElementById("changeRightTime")
        time="afternoon"
        changeLeftTime.classList.remove("changeTime")
        changeRightTime.classList.add("changeTime")
        let moneyContent=document.getElementById("moneyContent")
        let dollor="2500"
        moneyContent.textContent=dollor
    }
    // 切換圖片
    function leftImg(){
        let totalImg=document.getElementsByClassName("img_Content").length;
        let img_container_1=document.getElementById("img_container").children[0];
        let img_container=document.getElementById("img_container");
        let imgCenter=document.getElementById("imgCenter")
        if(img_container_1.classList.contains("display")==false){
            imgNumber=totalImg-1;
            img_container.children[0].classList.add("display")
            img_container.children[imgNumber].classList.remove("display");
            imgCenter.children[0].classList.remove("nowImg")
            imgCenter.children[imgNumber].classList.add("nowImg")
        }else{
            imgNumber-=1;
            img_container.children[imgNumber+1].classList.add("display")
            img_container.children[imgNumber].classList.remove("display"); 
            imgCenter.children[imgNumber+1].classList.remove("nowImg")
            imgCenter.children[imgNumber].classList.add("nowImg")
        };
    };
    function rightImg(){
        let img_container_1=document.getElementById("img_container").children[0];
        let img_container=document.getElementById("img_container");
        let imgCenter=document.getElementById("imgCenter")
        // 判斷是否為第一張照片顯示
        if(img_container_1.classList.contains("display")==false){
            // 判斷圖片不只1張
            if(data.data.images.length>1){
                imgNumber=1;
                img_container.children[imgNumber-1].classList.add("display");
                img_container.children[imgNumber].classList.remove("display");
                imgCenter.children[imgNumber-1].classList.remove("nowImg")
                imgCenter.children[imgNumber].classList.add("nowImg")
            };
        }else{
            imgNumber+=1;
            // 判斷是否為最後一張照片
            if(img_container.children[imgNumber]==null){
                img_container.children[imgNumber-1].classList.add("display");
                img_container.children[0].classList.remove("display");
                imgCenter.children[imgNumber-1].classList.remove("nowImg")
                imgCenter.children[0].classList.add("nowImg")
            }else{
                img_container.children[imgNumber-1].classList.add("display");
                img_container.children[imgNumber].classList.remove("display");
                imgCenter.children[imgNumber-1].classList.remove("nowImg")
                imgCenter.children[imgNumber].classList.add("nowImg")
            };
        };
    };
    // 抓取網址、連線api
    time="morning"
    let getdatareq=new XMLHttpRequest();
    getdatareq.open("get","/api"+location.pathname);
    getdatareq.onload=function(){
        data=JSON.parse(this.responseText);
        // 抓取id
        let name=document.getElementById("name");
        let transport=document.getElementById("transport");
        let description=document.getElementById("description");
        let address=document.getElementById("address");
        let category=document.getElementById("category");
        let img=document.getElementById("img");
        let img_container=document.getElementById("img_container");
        // 創造api文字
        let Name = document.createTextNode(data.data.name);
        let Description = document.createTextNode(data.data.description);
        let Address = document.createTextNode(data.data.address);
        let Transport = document.createTextNode(data.data.transport);
        // 判斷mrt是否為空值
        if(data.data.mrt==null){
            let Category = document.createTextNode(data.data.category);
            category.appendChild(Category);
        }else{
            let Category = data.data.category;
            let Mrt=data.data.mrt;
            let content=Category+" at "+Mrt;
            let Content = document.createTextNode(content);
            category.appendChild(Content);
        };
        imgAmount()
        // 填入api文字、圖片
        name.appendChild(Name);
        description.appendChild(Description);
        address.appendChild(Address);
        transport.appendChild(Transport);
        imgNumber=data.data.images.length;
        // 創造第一張圖片div
        let img_div=document.createElement("div");
        img_div.classList.add("img_Content");
        img_div.style.backgroundImage="url("+data.data.images[0]+")";
        img_container.appendChild(img_div);
        // 創造第二張圖片以後的div
        imgcount=1
        while(imgcount<imgNumber){
            let img_div=document.createElement("div");
            img_div.classList.add("img_Content");
            img_div.classList.add("display");
            img_div.style.backgroundImage="url("+data.data.images[imgcount]+")";
            img_container.appendChild(img_div);
            imgcount+=1;
        }
        //判斷交通方式是否為空值
        if(data.data.transport==null){
            let transportTitle=document.getElementById("transportTitle")
            let transport=document.getElementById("transport")
            transportTitle.innerHTML=""
            transport.innerHTML=""
        }   
        
    }
    getdatareq.send();

    function clickImg(){
        var img=document.getElementsByClassName("imgChoice")
        var index=[].indexOf.call(img[0].parentElement.children,img[0])
        var img=this
    }
    function imgAmount(){
        imgNumber=data.data.images.length;
        let whileNumber=0
        while(whileNumber<imgNumber){
            let newDiv=document.createElement("div");
            let imgCenter=document.getElementById("imgCenter");
            newDiv.classList.add("imgChoice");
            newDiv.setAttribute("onClick","clickImg()")
            imgCenter.appendChild(newDiv);
            whileNumber+=1;
        };
        let totalImg=document.getElementsByClassName("imgChoice");
        totalImg[0].classList.add("nowImg");
    };
  