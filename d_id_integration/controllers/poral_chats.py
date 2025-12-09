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

    @http.route(['/my/chats', '/my/chats/page/<int:page>'], type='http', auth='public', website=True) # auth -> public for not logged in users, auth -> user for logged in users
    def portal_chats_list_view(self, page=1, sortby='id', search="", search_in="All", **kwargs):
        sorted_list = {
            'id': {'label': 'Chat Desc', 'order': 'id desc'},
            'character_name': {'label': 'Character', 'order': 'character'},
            'question': {'label': 'Question', 'order': 'question'},
            'lyrics': {'label': 'Answer', 'order': 'lyrics'},
        }
        search_list = {
            'All': {'label': 'All', 'input': 'All', 'domain': []},
            'character': {'label': 'Character', 'input': 'character', 'domain': self._get_character_domain(search)},
            'question': {'label': 'Question', 'input': 'question', 'domain': [('question', 'ilike', search)]},
            'lyrics': {'label': 'Answer', 'input': 'lyrics', 'domain': [('lyrics', 'ilike', search)]},
        }
        search_domain = search_list[search_in]['domain']
        default_order_by = sorted_list[sortby]['order']
        user = request.env.user
        search_domain.append(('create_uid', '=', user.id)) # if I am not logged
        chat_count = request.env['d.id.api'].sudo().search_count(search_domain)
        page_detail = pager(url='/my/chats', total=chat_count, page=page, url_args={'sortby': sortby, 'search_in': search_in, 'search': search}, step=3)
        chats = request.env['d.id.api'].sudo().search(search_domain, limit=3, order= default_order_by ,offset=page_detail['offset'])
        values = {
            'page_name': 'chats',
            'chat_count': chat_count,
            'chats': chats,
            'pager': page_detail,
            'sortby': sortby,
            'searchbar_sortings': sorted_list,
            'search_in': search_in,
            'searchbar_inputs': search_list,
            'search': search,
        }
        return request.render('d_id_integration.portal_my_chats_list_view', values)

    @http.route(['/my/chats/<int:chat_id>'], type='http', auth='public', website=True)
    def portal_chats_form_view(self, chat_id, **kwargs):

        chat = request.env['d.id.api'].sudo().browse(chat_id)
        values = {
            'page_name': 'chat_form_view',
            'chat_id': chat_id,
            'chat': chat,
            'object': chat,
        }
        user = request.env.user
        chats = request.env['d.id.api'].sudo().search([
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

    @http.route(['/my/chats/print/<int:chat_id>'], type='http', auth='public', website=True)
    def portal_chats_report_view(self, chat_id, **kwargs):
        print("Hello From Report Screen", chat_id)

        # def _show_report(self, model, report_type, report_ref, download=False):
        chat = request.env['d.id.api'].browse(chat_id)
        return self._show_report(model=chat, report_type='pdf', report_ref='d_id_integration.report_did_api', download=True)

    def _get_character_domain(self, search):
        if not search:
            return []

        character_map = {
            'sara': 'ch1',
            'abeer': 'ch2',
        }

        search_lower = search.lower().strip()

        for name, key in character_map.items():
            if name in search_lower:
                return [('character', '=', key)]

        return [('character', '=', False)]