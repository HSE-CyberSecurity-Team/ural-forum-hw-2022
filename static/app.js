var servicesAmount = 0;

function service_elems(id, d) {
            // var link = document.createElement('div');
            // link.id = 'link_' + String(id);
            // link.innerHTML = "<input type=\"text\" style=\"width: 100%; visibility: visible;\" placeholder=\"Input a link to the service (e.g. https://www.google.com/)\">";
            // var name = document.createElement('div');
            // name.id= 'link_' + String(id);
            // name.innerHTML = "<input type=\"text\" style=\"width: 100%; visibility: visible;\" placeholder=\"Input a name of the service (e.g. google/)\">";
            // var button = document.createElement('div');
            // button.id= 'button_' + String(id);
            // button.innerHTML = "<input type=\"button\" value=\"Add\" style=\"width:100%;color:white;background-color:#4c9aff;visibility:hidden;\" onclick=\"addService()\">\n";
            var form = document.createElement("form"+id);
            // form.setAttribute("method", "post");
            // form.setAttribute("action", "submit.php");

            // Create an input element for emailID
            var name = document.createElement("input");
            name.setAttribute("value", d["name"])
            name.setAttribute("type", "text");
            name.setAttribute("name", "service_name_"+id);
            name.setAttribute("placeholder", "service_name_"+id);

            // Create an input element for password
            var url = document.createElement("input");
            url.setAttribute("value", d["url"])
            url.setAttribute("type", "text");
            url.setAttribute("name", "service_url_"+id);
            // url.setAttribute("id", )
            url.setAttribute("placeholder", "service_url_"+id);

            // Create a submit button
            var button = document.createElement("button");
            button.setAttribute("name", "button_"+id);
            button.setAttribute("placeholder", "update")
            button.setAttribute("id", String(id))
            button.setAttribute("onclick", "addNewService(this.id)")
            // s.setAttribute("value", "Submit");

            // Append the email_ID input to the form
            form.append(name);
            form.append(url);
            form.append(button);

            document.getElementsByClassName("timeframes-container")[0].appendChild(form);
            servicesAmount += 1
            // document.getElementById("text1").style.visibility = "visible";

            // document.getElementById("pushMe2").style.visibility = "visible";
            // return [link, name, button]
        }

function get_apps(){
    $.ajax
    ({
        type: "GET",
        url: 'http://127.0.0.1:8000/app_lists',
        contentType:"application/json; charset=utf-8",
        // headers: {"Access-Control-Allow-Origin":"*"},
        // dataType: 'json',

        // async: false,
        // data: '{"name": "' + document.getElementById("text1").value + '", "url" : "' + document.getElementById("text1").value + '", "active" : "true"}',
        success: function (d) {
            servicesAmount = 0;
            // console.log(d)
            alert(JSON.stringify(d));
            let container = document.getElementById("timeframes-container")
            for (var i = 0; i < d.length; i++){
                // let elems = service_elems(i);
                // console.log(elems)
                // container.appendChild(elems[0]);
                // container.appendChild(elems[1]);
                // container.appendChild(elems[2]);
                service_elems(i, d[i]);
                // servicesAmount += 1;
            }
        },
        error: function (e){
          alert('lol')
        }
    })
}
function get_health(app){
    $.ajax
    ({
        type: "GET",
        url: 'http://127.0.0.1:8000/health/' + app,
        contentType:"application/json; charset=utf-8",
        // headers: {"Access-Control-Allow-Origin":"*"},
        // dataType: 'json',

        // async: false,
        // data: '{"name": "' + document.getElementById("text1").value + '", "url" : "' + document.getElementById("text1").value + '", "active" : "true"}',
        success: function (d) {
            // console.log(d)
            alert(JSON.stringify(d));

        },
        error: function (e){
          alert('error')
        }
    })
}


// get_apps()
window.onload = get_apps;

function showAddMenu(){
    service = {"name": "", "url": "", "active": true}
    service_elems(servicesAmount, service)
}

function addNewService(clicked_id){
    // alert('adding new service for button ' + clicked_id)

    var name = document.getElementsByName("service_name_" + clicked_id)[0].value;

    var url = document.getElementsByName("service_url_" + clicked_id)[0].value;

    if(name.length === 0 || url.length === 0)
    {
        document.getElementById("text1").value = "Oops, blank input...";
        alert("Поле пустое - пожалуйста, введите ссылку на cервис и название")
    } else {

        $.ajax
        ({
            type: "POST",
            url: 'http://127.0.0.1:8000/add',
            contentType:"application/json; charset=utf-8",
            // headers: {"Access-Control-Allow-Origin":"*"},
            dataType: 'json',

            async: false,
            data: '{"name": "' + name + '", "url" : "' + url + '", "active" : "true"}',
            success: function (data) {

                // alert("Thanks!");
                if (data === "app already exists"){
                    get_health(name)
                }
            }
        })
    }
}