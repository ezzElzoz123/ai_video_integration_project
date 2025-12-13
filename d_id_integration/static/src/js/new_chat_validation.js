odoo.define("d_id_integration.NewChatForm", function(require){
'use strict';

var publicWidget = require("web.public.widget");
publicWidget.registry.NewChatForm = publicWidget.Widget.extend({
    selector:"#new_chat_creation",
    events:{
    'submit': "_onSubmitButton"
    },

    _onSubmitButton: function(evt){
        var question = this.$("input"[name='question']).val();
        var $characterName = this.$("select"[name='character']);
        var character_name = ($characterName.val() || '0');
        var valid_characters = ['ch1', 'ch2'];

//        console.log("Hello from js after submit button clicked");
//        alert("HI");

        if (!question){
            $("#chat_client_side_validation_message").html("Please enter question.");
            $("#chat_client_side_validation_message").show();
            evt.preventDefault();
        }
        if (!character_name || character_name == '0'){
            $("#chat_client_side_validation_message").html("Please select character.");
            $("#chat_client_side_validation_message").show();
            evt.preventDefault();
        }
        if (valid_characters.indexOf(character_name) === -1){
                $("#chat_client_side_validation_message").html("Invalid character selection.");
                $("#chat_client_side_validation_message").show();
                evt.preventDefault();
            }
    }
})

});