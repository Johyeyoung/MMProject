from flask_admin.contrib.sqla import ModelView
from flask_admin.helpers import get_redirect_target
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_admin.babel import gettext, ngettext
from flask_admin.contrib.sqla import form, filters as sqla_filters, tools

from flask import (current_app, request, redirect, flash, abort, json,
                   Response, get_flashed_messages, stream_with_context)
from flask_admin_subview import SubviewContainerMixin, SubviewEntry
from .formatters import *


# SubviewContainerMixin -> 딜 세부 페이지 html 담당
class OptionView(SubviewContainerMixin, ModelView):

    can_view_details = True
    # ModelView에서 제공하는 edit, delete, create 아이콘 지우기
    can_delete, can_edit, can_create = False, False, False

    #http://localhost:5000/deal/?search=KR4201S82224 -> search로 필드 넣을떄
    column_searchable_list = ("inisCd",)  # 검색가능한 필드  -> 세부정보에 추가
    column_sortable_list = ("inisType", 'insId', "posType", 'matDt', 'atmCd', 'strike', 'status', 'baseDt')
    column_filters = ("inisType", "inisCd", 'insId', "posType", 'matDt', 'atmCd', 'strike', 'baseDt')

    column_formatters = {
        # a href 관련 칼럼 생성
        "inisCdHref": model_link_formatter_inisCd(section="option", attr=""),
        "insIdHref": model_link_formatter_insId(section="underlying", attr=""),
        "opstInisCdHref": model_link_formatter_opstInisCd(section="option", attr=""),
    }
    column_list = ("inisCdHref", "inisNm", "inisType", 'insIdHref', "posType", 'matDt', 'matdtIdx', 'atmCd', 'strike', 'status', 'baseDt')
    column_labels = {"inisCdHref": '종목코드', "inisNm": '종목명', "inisType": "타입",
                     'insIdHref': '기초자산ID', 'posType': 'Pos', 'matDt': '만기일자',  'matdtIdx': '월물정보',
                     'atmCd': 'ATM코드', 'strike': '행사가격', 'status': '딜상태', 'baseDt': '생성일자'
                     }
    column_details_list = ("inisCd",)
    form_create_rules = ("inisCd",)
    form_edit_rules = form_create_rules

    _extra_js = ("/static/reloader.js",)


    # 종목 세부페이지 URL처리
    from flask_admin.base import expose
    @expose('/details/')
    def details_view(self):
        """
            Details model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_view_details:
            return redirect(return_url)
        id = get_mdict_item_or_list(request.args, 'id')
        baseDt = get_mdict_item_or_list(request.args, 'baseDt')

        model = self.session.query(self.model).filter(self.model.baseDt == baseDt, self.model.inisCd == id).first()
        if model is None:
            flash(gettext('Record does not exist.'), 'error')
            return redirect(return_url)

        if self.details_modal and request.args.get('modal'):
            template = self.details_modal_template
        else:
            template = self.details_template

        return self.render(template,
                           model=model,
                           details_columns=self._details_columns,
                           get_value=self.get_detail_value,
                           return_url=return_url)