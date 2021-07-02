function start(){
    checkMember()
}
function submit(){
    let date=document.getElementById("dateInput").value
    let price=parseInt(document.getElementById("moneyContent").textContent)
    let attractionId=parseInt(location.pathname.slice(12))
    let img=document.getElementById("img_container").children[0].style.backgroundImage
    let name=document.getElementById("name").textContent
    let address=document.getElementById("address").textContent
    if (date==""){
        alert("請選取日期")
    }else{
        let bookingreq=new XMLHttpRequest()
        bookingreq.open("post","/api/booking")
        bookingreq.onload=function(){
            bookingData=JSON.parse(this.responseText);
            if (bookingData["message"]=="使用者未登入"){
                signinWindow();
            }else if (bookingData["ok"]==true){
                window.sessionStorage.setItem("name",name)
                window.sessionStorage.setItem("address",address)
                window.sessionStorage.setItem("date",date)
                window.sessionStorage.setItem("time",time)
                window.sessionStorage.setItem("price",price)
                window.sessionStorage.setItem("img",img)
                window.location.href="/booking"
            }else if(bookingData["message"]=="訂購資料有缺誤"){
                alert("訂購資料有缺誤")
            }
            
        }
        bookingreq.send(JSON.stringify({"attractionId":attractionId,"date":date,"time":time,"price":price}))
    }
}
// 預定行程按鈕
function bookingBut(){
    let headsignout=document.getElementById("headsignout").className
    if (headsignout=="mymouse"){
        window.location.href="/booking"
    }else{
        signinWindow()
    }
}

//確認使用者登入狀態 
function checkMember(){
        let reqMember=new XMLHttpRequest();
        reqMember.open("get","/api/user")
        reqMember.onload=function(){
            let getdata=JSON.parse(this.responseText);
            let headsignin=document.getElementById("headsignin")
            let headsignout=document.getElementById("headsignout")
            if(getdata["data"]!=null){
                headsignin.classList.add("display")
                headsignout.classList.remove("display")
                headsignin.style.display="none"

            }else{
                headsignin.classList.remove("display")
                headsignout.classList.add("display")
                headsignout.style.display="none"

            }
        }
        reqMember.send()
}
// function clickHam(){
//     let headRight=document.getElementById("headRight")
//     headRight.classList.toggle("display")
// }
// function width(){
//     let width=document.documentElement.clientWidth
//     // let width=window.screen.width
//     if(width<600){
//         let headRight=document.getElementById("headRight")
//         headRight.classList.add("display")
//     }else{
//         let headRight=document.getElementById("headRight")
//         headRight.classList.remove("display")
//     }
// }

//登出
function signOut(){
    let reqsignOut=new XMLHttpRequest()
    reqsignOut.open("delete","/api/user")
    reqsignOut.onload=function(){
        window.location.reload()
        headsignin.classList.remove("display")
        headsignout.classList.add("display")
        
    }
    reqsignOut.send()
}    
// 登入
function signIn(){
    let signineMail=document.getElementById("signinEmail").value
    let signinPassword=document.getElementById("signinPassword").value
    let signinError=document.getElementById("signinError")
    if(signineMail==""|signinPassword==""){
        signinError.classList.remove("display")
    }else{
        let reqsignIn=new XMLHttpRequest()
        reqsignIn.open("post","/api/user")
        reqsignIn.onload=function(){
            signindata=JSON.parse(this.responseText);
            if (signindata["ok"]==true){
                window.location.reload()
            }else{
                signinError.classList.remove("display")
                console.log(signindata)
            }
            
        }
        reqsignIn.send(JSON.stringify({"email":signineMail,"password":signinPassword}))
    }
}  
//註冊
function signUp(){
    let signupName=document.getElementById("signupName").value
    let signupMail=document.getElementById("signupEmail").value
    let signupPassword=document.getElementById("signupPassword").value
    let signupemailError=document.getElementById("signupemailError")
    let signupspaceError=document.getElementById("signupspaceError")
    // 判斷input是否空白
    if(signupName==""| signupMail==""| signupPassword==""){
        signupspaceError.classList.remove("display")
    }else{
        // 連接註冊API
        let reqsignUp=new XMLHttpRequest();
        reqsignUp.open("post","/api/user")
        reqsignUp.onload=function(){
            signupdata=JSON.parse(this.responseText);
            if(signupdata["ok"]==true){
                //註冊成功則自動登入
                let reqsignIn=new XMLHttpRequest()
                reqsignIn.open("post","/api/user")
                reqsignIn.onload=function(){
                    signindata=JSON.parse(this.responseText);
                    if (signindata["ok"]==true){
                        window.location.reload()
                    }else{
                        let signinError=document.getElementById("signinError")
                        signinError.classList.remove("display")
                    }
                    
                }
                reqsignIn.send(JSON.stringify({"email":signupMail,"password":signupPassword}))
            }else{
                // 註冊失敗顯示原因
                signupspaceError.classList.add("display")
                signupemailError.classList.remove("display")
            }
        }
        reqsignUp.send(JSON.stringify({"name":signupName,"email":signupMail,"password":signupPassword}))

    }
    

}
// 註冊、登入視窗
function signinWindow(){
    let signIn=document.getElementById("signIn");
    let signUp=document.getElementById("signUp");
    let windowBackground=document.getElementById("windowBackground")
    windowBackground.classList.remove("display");
    signUp.classList.add("display");
    signIn.classList.remove("display");
    // 隱藏錯誤訊息
    signinError.classList.add("display");
    signupspaceError.classList.add("display");
    signupemailError.classList.add("display");
}
function signupWindow(){
    let signIn=document.getElementById("signIn");
    let signUp=document.getElementById("signUp");
    windowBackground.classList.remove("display");
    signUp.classList.remove("display");
    signIn.classList.add("display");
    // 隱藏錯誤訊息
    signinError.classList.add("display");
    signupspaceError.classList.add("display");
    signupemailError.classList.add("display");
}
function closeWindow(){
    let signIn=document.getElementById("signIn");
    let signUp=document.getElementById("signUp");
    windowBackground.classList.add("display");
    signUp.classList.add("display");
    signIn.classList.add("display");
    // 隱藏錯誤訊息
    signupspaceError.classList.add("display");
    signupemailError.classList.add("display");
}



