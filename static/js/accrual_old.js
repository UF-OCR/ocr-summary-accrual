         $( "#LoadingScreen" ).hide();
         $( "#results" ).hide();
         $( "#errors" ).hide();
         $( "#sendAccrual" ).hide();
         $( "#errorMsg" ).hide();
         $( "#successMsg" ).hide();
         $( "#showData" ).hide();
         $("#dynamic").attr("style", "display:none")
         $( "#upload" ).click(function() {
                    var current_progress = 0;
                        var interval = setInterval(function() {
                            if (current_progress >= 100){
                                $("#dynamic").attr("style", "display:none")
                                $("#dynamic")
                                    .css("width", "100%")
                                    .attr("aria-valuenow", 100)
                                    .text("90% Complete");
                            }else{
                                  $("#dynamic").attr("style", "display:block")
                                  current_progress += 10;
                                  $("#dynamic")
                                  .css("width", current_progress + "%")
                                  .attr("aria-valuenow", current_progress)
                                  .text(current_progress + "% Complete");
                            }
                        }, 1000);
          });

           $( "#sendAccrual1" ).click(function() {
                $( "#successMsg" ).hide();
                $( "#errorMsg" ).hide();
                     $.ajax({
                          url: "/authenticate",
                          data: JSON.stringify({'username':$('#username').val(), 'password':$('#password').val(),'protocolNo':$('#protocolNoVal').val()}) ,
                          contentType: 'application/json',
                          type:'POST'
                        }).done(function(data) {
                           if(data == "Authenticated"){
                                $( "#sendAccrual1" ).hide();
                                $( "#sendAccrual" ).show();
                                $( "#successMsg" ).show();
                           }else{
                                $( "#errorMsg" ).show();
                           }
                        }).fail(function(xhr, err) {
                            var responseTitle= $(xhr.responseText).filter('title').get(0);
                            alert($(responseTitle).text() + "\n" + formatErrorMessage(xhr, err))
                        });
            });
            $( "#sendAccrual" ).click(function() {
                        $( "#LoadingScreen" ).show();
                        $( "#resultDiv" ).hide();
                        $( "#firstStep" ).hide();
                        var current_progress = 0;
                        var interval = setInterval(function() {
                            if (current_progress >= 100){
                                $("#dynamic").attr("style", "display:none")
                                $("#dynamic")
                                    .css("width", "100%")
                                    .attr("aria-valuenow", 100)
                                    .text("100% Complete");
                            }else{
                                  $("#dynamic").attr("style", "display:block")
                                  current_progress += 10;
                                  $("#dynamic")
                                  .css("width", current_progress + "%")
                                  .attr("aria-valuenow", current_progress)
                                  .text(current_progress + "% Complete");
                            }
                        }, 500);
                        $.ajax({
                          url: "/addAccruals",
                          data: JSON.stringify({'username':$('#username').val(), 'password':$('#password').val(), 'result': $('#parsedJson').text()}) ,
                          contentType: 'application/json',
                          type:'POST'
                        }).done(function(data) {
                            $( "#firstStep" ).hide();
                            current_progress = 100;
                            $("#dynamic")
                                .css("width", "100%")
                                .attr("aria-valuenow", 100)
                                .text("100% Complete");
                            $("#dynamic").attr("style", "display:none")
                            $( "#showData" ).show();
                            $( "#results" ).show();
                            $( "#resultData" ).html(data);
                        }).fail(function(xhr, err) {
                            $( "#firstStep" ).hide();
                            current_progress = 100;
                            $("#dynamic")
                                .css("width", "100%")
                                .attr("aria-valuenow", 100)
                                .text("100% Complete");
                            $("#dynamic").attr("style", "display:none")
                            $( "#showData" ).show();
                            var responseTitle= $(xhr.responseText).filter('title').get(0);
                            $( "#errors" ).show();
                            $( "#errorData" ).html($(responseTitle).text() + "\n" + formatErrorMessage(xhr, err));

                        });
            });
            function formatErrorMessage(jqXHR, exception) {
                if (jqXHR.status === 0) {
                    return ('Not connected.\nPlease verify your network connection.');
                } else if (jqXHR.status == 404) {
                    return ('The requested page not found. [404]');
                } else if (jqXHR.status == 500) {
                    return ('Internal Server Error [500].');
                } else if (exception === 'parsererror') {
                    return ('Requested JSON parse failed.');
                } else if (exception === 'timeout') {
                    return ('Time out error.');
                } else if (exception === 'abort') {
                    return ('Ajax request aborted.');
                } else {
                    return ('Uncaught Error.\n' + jqXHR.responseText);
                }
            }