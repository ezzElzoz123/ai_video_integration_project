from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalChats(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        if 'chat_count' in counters:
            chat_count = request.env['d.id.api'].search_count([
                ('create_uid', '=', request.env.user.id)
            ])
            values['chat_count'] = chat_count
        return values

    @http.route(['/my/chats'], type='http', website=True)
    def portal_chats_list_view(self, **kwargs):
        user = request.env.user
        chat_count = request.env['d.id.api'].search_count([
            ('create_uid', '=', user.id)
        ])
        chats = request.env['d.id.api'].search([
            ('create_uid', '=', user.id)
        ])
        values = {
            'page_name': 'chats',
            'chat_count': chat_count,
            'chats': chats,
        }
        return request.render('d_id_integration.portal_my_chats_list_view', values)

    @http.route(['/my/chats/<int:chat_id>'], type='http', website=True)
    def portal_chats_form_view(self, chat_id, **kwargs):
        chat = request.env['d.id.api'].sudo().browse(chat_id)

        if not chat.exists() or chat.create_uid.id != request.env.user.id:
            return request.redirect('/my/chats')

        values = {
            'page_name': 'chat_form_view',
            'chat_id': chat_id,
            'chat': chat,
            # 'no_breadcrumbs': True,  # ✅ عشان يقلل المشاكل
        }

        # ✅ استخدم render مباشر بدون assets زيادة
        return request.render(
            'd_id_integration.portal_chat_page_form_view',
            values,
            headers={'X-Frame-Options': 'SAMEORIGIN'}
        )