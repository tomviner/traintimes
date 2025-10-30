from traintimes.models import LocationResponse


def test_location_response_coerces_null_services_to_empty_list():
    payload = {
        'location': {
            'name': 'Highbury & Islington',
            'crs': 'HIB',
            'tiploc': 'HIBURY',
        },
        'filter': None,
        'services': None,
    }

    response = LocationResponse.model_validate(payload)

    assert response.services == []


def test_location_response_preserves_existing_service_list():
    payload = {
        'location': {
            'name': 'Highbury & Islington',
            'crs': 'HIB',
            'tiploc': 'HIBURY',
        },
        'filter': None,
        'services': [
            {
                'locationDetail': {
                    'realtimeActivated': True,
                    'tiploc': 'HIBURY',
                    'crs': 'HIB',
                    'description': 'Highbury & Islington',
                    'origin': [],
                    'destination': [],
                },
                'serviceUid': 'A12345',
                'runDate': '2024-01-01',
                'serviceType': 'train',
                'isPassenger': True,
                'atocCode': 'ZZ',
                'atocName': 'Zed Rail',
            }
        ],
    }

    response = LocationResponse.model_validate(payload)

    assert len(response.services) == 1
    assert response.services[0].service_uid == 'A12345'
