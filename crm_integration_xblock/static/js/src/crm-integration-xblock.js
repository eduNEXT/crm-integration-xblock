/* Javascript for CrmIntegration. */
var crmIntegration = {
  // Example of request success handler function
  xhrHandler: function xhrHandler(data) {
    console.log("Handler callback was called");
  },
};

function CrmIntegrationLms(runtime, element) {
    console.log("Initializing the js code at the LMS");

    var handlerUrl = runtime.handlerUrl(element, 'send_crm_data');
    console.log("The handler url: " + handlerUrl);

    $.ajax({
        type: "POST",
        url: handlerUrl,
        data: JSON.stringify({"hello": "world"}),
        success: crmIntegration.xhrHandler()
    });

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}

function CrmIntegrationStudio(runtime, element) {
    console.log("Initializing the js code in Studio");

    var handlerUrl = runtime.handlerUrl(element, 'send_crm_data');
    console.log("The handler url: " + handlerUrl);

    $.ajax({
        type: "POST",
        url: handlerUrl,
        data: JSON.stringify({"hello": "world"}),
        success: crmIntegration.xhrHandler()
    });

    $(function ($) {
        /* Here's where you'd do things on page load. */
    });
}
