from PIL.ImageChops import offset

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager


class PortalChats(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        if 'chat_count' in counters:
            chat_count = request.env['d.id.api'].search_count([
                ('create_uid', '=', request.env.user.id)
            ])
            values['chat_count'] = chat_count
        return values

    @http.route(['/my/chats', '/my/chats/page/<int:page>'], type='http', website=True)
    def portal_chats_list_view(self, page=1, **kwargs):
        user = request.env.user
        chat_count = request.env['d.id.api'].search_count([
            ('create_uid', '=', user.id)
        ])
        page_detail = pager(url='/my/chats', total=chat_count, page=page, step=3)
        chats = request.env['d.id.api'].search([
            ('create_uid', '=', user.id)
        ], limit=3, offset=page_detail['offset'])
        values = {
            'page_name': 'chats',
            'chat_count': chat_count,
            'chats': chats,
            'pager': page_detail,
        }
        return request.render('d_id_integration.portal_my_chats_list_view', values)

    @http.route(['/my/chats/<int:chat_id>'], type='http', website=True)
    def portal_chats_form_view(self, chat_id, **kwargs):

        chat = request.env['d.id.api'].sudo().browse(chat_id)
        values = {
            'page_name': 'chat_form_view',
            'chat_id': chat_id,
            'chat': chat,
        }
        user = request.env.user
        chats = request.env['d.id.api'].search([
            ('create_uid', '=', user.id)
        ])
        chat_ids = chats.ids
        chat_index = chat_ids.index(chat.id)
        if chat_index != 0 and chat_ids[chat_index-1]:
            values['prev_record'] = '/my/chats/{}'.format(chat_ids[chat_index-1])
        if chat_index < len(chat_ids) -1 and chat_ids[chat_index+1]:
            values['next_record'] = '/my/chats/{}'.format(chat_ids[chat_index+1])
        if not chat.exists() or chat.create_uid.id != request.env.user.id:
            return request.redirect('/my/chats')

        return request.render(
            'd_id_integration.portal_chat_page_form_view',
            values,
            headers={'X-Frame-Options': 'SAMEORIGIN'}
        )