# -*- coding: utf-8 -*-

import json

# from database import db
# from test.conftest import DefaultOut
from config.app_mdl import cfg


def test_err_add_json(client):
    """В базу не записан JSON"""
    db.sp_certificate_imdm_authentication.return_value = DefaultOut(0, ''),
    db.sp_kit_imdm_get.return_value = DefaultOut(0, ''), ['любая хрень']
    body = [
        {
            "channel": "MDM",
            "event": {
                "serializedType": "EventIpAddress",
                "event_format_version": 1,
                "event_code": 89,
                "event_uuid": "080ba608-58c4-4221-ac9b-9cadccba716d",
                "network_type": "wifi",
                "ip_address": "192.168.10.11"
            },
            "timestamp": 1669730657751
        }
    ]
    db.sp_event_imdm_add_connect.return_value = DefaultOut(0, ''),
    db.sp_monitor_imdm_set_mob_param.return_value = DefaultOut(-11901, 'Operation system platform not found'),
    db.sp_event_imdm_add_json.return_value = DefaultOut(-3303, 'Device params not registered: Device not found'),

    response = client.post(
        "/api/v1/events",
        headers={'X-MCC-ID': '102500', 'Content-Type': 'application/json', 'user-agent': 'Guardliner/1.0 (ABCD002F)'},
        content=json.dumps(body)
    )
    assert response.status_code == 201, "События не сериализованы и/или не записаны в БД"
    assert response.content.decode() == 'OK', "в body должны быть чистые байты b'OK'"


def test_correct_body(client):
    """Нормальное завершение + браслет"""
    db.sp_certificate_imdm_authentication.return_value = DefaultOut(0, ''),
    db.sp_kit_imdm_get.return_value = DefaultOut(0, ''), ['любая хрень']
    body = [
        {
            "channel": "MDM",
            "event": {
                "serializedType": "EventAppInstall",
                "event_format_version": 2,
                "event_code": 3,
                "event_uuid": "54b3e190-4662-4a5a-a9eb-d3225799898d",
                "app": {
                    "can_delete": 0,
                    "can_disable": 0,
                    "enabled": 1,
                    "is_managed": 1,
                    "type": "corporate",
                    "name": "Монитор",
                    "uid": "ru.niisokb.mcc",
                    "version_code": 7000005,
                    "version_name": "7.0.0.5"
                }
            },
            "timestamp": 1669730657542
        },
        {
            "channel": "MDM",
            "event": {
                "serializedType": "EventIpAddress",
                "event_format_version": 1,
                "event_code": 89,
                "event_uuid": "080ba608-58c4-4221-ac9b-9cadccba716d",
                "network_type": "wifi",
                "ip_address": "192.168.10.11"
            },
            "timestamp": 1669730657751
        }
    ]
    db.sp_event_imdm_add_connect.return_value = DefaultOut(0, ''),
    db.sp_monitor_imdm_set_mob_param.return_value = DefaultOut(0, ''),
    db.sp_event_imdm_add_json.return_value = DefaultOut(0, ''),

    response = client.post(
        "/api/v1/events",
        headers={'X-MCC-ID': '102500', 'Content-Type': 'application/json', 'user-agent': 'Guardliner/1.0 (ABCD002F)'},
        content=json.dumps(body)
    )
    assert response.status_code == 201, "События не сериализованы и/или не записаны в БД"
    assert response.content.decode() == 'OK', "в body должны быть чистые байты b'OK'"


def test_logical_err(client):
    """Логические ошибки в запросе"""
    db.sp_certificate_imdm_authentication.return_value = DefaultOut(0, ''),
    db.sp_kit_imdm_get.return_value = DefaultOut(0, ''), ['любая хрень']
    body = [{"ERROR_it_is_not_key_event": "any_value"}, "ERROR_it_is_not_dict"]
    db.sp_event_imdm_add_connect.return_value = DefaultOut(0, ''),
    db.sp_monitor_imdm_set_mob_param.return_value = DefaultOut(-11901, 'Operation system platform not found'),
    db.sp_event_imdm_add_json.return_value = DefaultOut(-3303, 'Device params not registered: Device not found'),

    response = client.post(
        "/api/v1/events",
        headers={'X-MCC-ID': '102500', 'Content-Type': 'application/json', 'user-agent': 'Guardliner/1.0 (ABCD002F)'},
        content=json.dumps(body)
    )
    assert response.status_code == 400, "На вход подано некорректное событие"


def test_invalid_json(client):
    """Некорректный JSON"""
    db.sp_certificate_imdm_authentication.return_value = DefaultOut(0, ''),
    db.sp_kit_imdm_get.return_value = DefaultOut(0, ''), ['любая хрень']
    body = ['{"any_key": "any_value"}, invalid_json']
    db.sp_event_imdm_add_connect.return_value = DefaultOut(0, ''),
    db.sp_monitor_imdm_set_mob_param.return_value = DefaultOut(0, ''),
    db.sp_event_imdm_add_json.return_value = DefaultOut(0, ''),

    response = client.post(
        "/api/v1/events",
        headers={'X-MCC-ID': '102500', 'Content-Type': 'application/json', 'user-agent': 'Guardliner/1.0 (ABCD002F)'},
        content=json.dumps(body)
    )
    assert response.status_code == 400, "На вход подан некорректный JSON"


def test_mTLS_cert_missing(client):
    """Нет сертификата mTLS"""
    config.sowa = False
    db.sp_certificate_imdm_authentication.return_value = DefaultOut(-20001, 'Certificate not found (Серт не найден)'),
    db.sp_kit_imdm_get.return_value = DefaultOut(0, ''), ['любая хрень']
    body = {
        "channel": "MDM",
        "event": {"serializedType": "EventIpAddress", "event_format_version": 1, "event_code": 89,
                  "event_uuid": "1eb37572-9c2f-4557-aaee-3daa9e9bb974", "network_type": "wifi",
                  "ip_address": "10.17.15.142"}, "timestamp": 1704800085633
    }
    db.sp_event_imdm_add_connect.return_value = DefaultOut(0, ''),
    db.sp_monitor_imdm_set_mob_param.return_value = DefaultOut(0, ''),
    db.sp_event_imdm_add_json.return_value = DefaultOut(0, ''),

    response = client.post(
        "/api/v1/events",
        headers={'X-MCC-ID': '102500', 'Content-Type': 'application/json', 'user-agent': 'Guardliner/1.0 (ABCD002F)'},
        content=json.dumps([body])
    )
    assert response.status_code == 401, "Отсутствует сертификат mTLS"
