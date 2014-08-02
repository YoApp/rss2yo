function submit(){
    var url = $("#url").val();
    var api = $("#apikey").val();
    
    $("#submit").attr("disabled", "true");
    $("#submit").text("Working ...")
    
    $.ajax({url:"/", data:{url:url, apikey:api}, type:"POST", success: function(data){
        $("#submit").removeAttr("disabled")
        $("#submit").text("Yo!")
        
        j = JSON.parse(data);
        console.log(j)
        
        if (j['error'] != undefined){
            $("#error").text(j['error'])
            
        } else { 
            $("#error").text("Successfully added!")
            $("#url").val('');
        }
        
        $("#error").slideDown()
        
    }})

}

function reset(){
    var api = $("#reset-api").val();
    
    $("#reset").attr("disabled", "true");
    $("#reset").text("Working ...")
    
    $.ajax({url:"/delete", data:{apikey:api}, type:"POST", success: function(data){
        
        $("#reset").removeAttr("disabled")
        $("#reset").text("Yo!")
        
        j = JSON.parse(data);
        console.log(j)
        
        if (j['error'] != undefined){
            $("#error").text(j['error'])
            
        } else { 
            $("#error").text("Success!")
        }
        
        $("#error").slideDown()
        
    }})
}