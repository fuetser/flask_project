function subscribeToGroup(groupId) {
    $.ajax({
        url: `/group/${groupId}/subscribe`,
        type: "POST",
        success: function(response) {
            if (response.isSubscribed) {
                $("#subscribeButton").text("Отписаться");
                $("#subscribeButton").removeClass("active");
            }
            else {
                $("#subscribeButton").text("Подписаться");
                $("#subscribeButton").addClass("active");
            }

            $("#subscribersCounter").text(response.subscribersCount)
            $("#subscribersDescription").text(response.subscribers)
         },
        error: function (request, status, error) {
            console.log(error)
        },
    })
}

function deleteGroup(groupId, endpoint) {
    $.ajax({
        url: `/group/${groupId}`,
        type: "DELETE",
        success: responce => {
            document.location.href = endpoint
        },
        error: (request, status, error) => {
            console.log(error)
        }
    })
}
