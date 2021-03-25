import json
from flask import request, send_file, jsonify, send_from_directory
import time
from .models import Scan, Events, ScanEvents
from lxml import etree
from driverapp import db, MEDIA_FOLDER
import uuid
import re
import base64
import traceback
from driverapp.helpers.script import NessusDriverScript
from flask.views import MethodView


class HomeView(MethodView):

    def __init__(self):
        self.response = dict()

    def get(self):
        self.response['success'] = True
        self.response['message'] = 'Nessus Driver App is Running'
        return jsonify(self.response)


class DownloadFile(MethodView):

    def __init__(self):
        pass

    def get(self, filename):
        return send_from_directory(MEDIA_FOLDER, filename, as_attachment=True)


class CreateScan(MethodView):

    def __init__(self):
        self.response = list()

    def post(self):
        # response = list()

        try:
            requestResponse = request.get_json()
        except Exception as e:
            # requestResponse = None
            return jsonify(e)

        targets = requestResponse.get("ips")
        redtree_event_id = int(requestResponse.get('redtree_event_id'))
        allowed_hosts = int(requestResponse.get("max_simul_hosts"))

        try:
            events = Events(redtree_event_id=redtree_event_id,
                            event_status='Received')
            db.session.add(events)
            db.session.commit()

            if len(targets) <= allowed_hosts:
                resp = dict()
                id = str(uuid.uuid4())
                scan_name = '{} {}'.format(requestResponse.get('client_name'), id)
                ips = ",".join(targets)
                # script.add_data(ips, req, name)
                scan = Scan(id=id, targets=ips, scan_name=scan_name,
                            nessus_url=requestResponse.get("url"),
                            nessus_username=requestResponse.get("username"),
                            nessus_password=requestResponse.get("password"),
                            scan_type=requestResponse.get('scan_type'),
                            status='Queued',
                            scan_message ='Scan added to driver',
                            event_id=events.id)
                db.session.add(scan)
                db.session.commit()
                resp["scan_name"] = scan.scan_name
                resp["targets"] = ips
                resp["scan_id"] = scan.id
                resp["scan_status"] = scan.status
                resp["scan_type"] = scan.scan_type
                resp['scan_message'] = scan.scan_message
                self.response.append(resp)
            else:
                for i in range(0, len(targets)+1, allowed_hosts):
                    resp = dict()
                    target = targets[i:i + allowed_hosts]
                    id = str(uuid.uuid4())
                    scan_name = '{} {}'.format(requestResponse.get('client_name'), id)
                    ips = ",".join(target)
                    # script.add_data(ips, req, name)
                    scan = Scan(id=id, targets=ips, scan_name=scan_name,
                                nessus_url=requestResponse.get("url"),
                                nessus_username=requestResponse.get("username"),
                                nessus_password=requestResponse.get("password"),
                                scan_type=requestResponse.get("scan_type"),
                                status='Queued',
                                scan_message ='Scan added to driver',
                                event_id=events.id)
                    db.session.add(scan)
                    db.session.commit()
                    resp["scan_name"] = scan.scan_name
                    resp["targets"] = ips
                    resp["scan_id"] = scan.id
                    resp["scan_status"] = scan.status
                    resp["scan_type"] = scan.scan_type
                    resp['scan_message'] = scan.scan_message
                    self.response.append(resp)
        except Exception as e:
            resp = {"id": None, 
                    "name": None, 
                    "targets": None, 
                    "error":e
                }
            self.response.append(resp)

        return jsonify(self.response)


class GetScan(MethodView):

    def __init__(self):
        pass
    
    def get(self, scan_id):

        data = {"name": None, "status": 'Running', "result": None}

        try:
            scan = Scan.query.get(scan_id)
        except:
            scan = None

        if scan:
            if scan.status != "Completed":
                try:
                    nessus_script = NessusDriverScript(scan)
                    nessus_script.get_status()
                except:
                    pass
            else:
                data['status'] = scan.status

            if scan.result != 'False':
                file_path = scan.result
                data["scan_id"] = scan.id
                data["name"] = scan.scan_name
                data["status"] = scan.status
                with open(file_path, 'rb') as file:
                    nessus_file = base64.b64encode(file.read())
                    data['result'] = nessus_file

        return jsonify(data)


class NessusJobs(MethodView):

    def __init__(self):
        pass

    def get(self, scan_id=None):
        response = list()
        if scan_id:
            resp = dict()
            scan = Scan.query.filter_by(id=scan_id).first()
            if scan:
                resp['scan_id'] = scan.id
                resp['time_started'] = scan.created
                resp['scan_type'] = scan.scan_type
                resp['status'] = scan.status
                resp['scan_message'] = scan.scan_message
                scan_selenium_logs = ScanEvents.query.filter_by(scan_id=scan.id).first()
                if scan_selenium_logs:
                    resp['selenium_logs'] = scan_selenium_logs.scan_event_history
                else:
                    resp['selenium_logs'] = ''

                event = Events.query.filter_by(id=scan.event_id).first()
                if event:
                    resp['redtree_event_id'] = event.redtree_event_id
                    resp['nessus_event_status'] = event.event_status

                return jsonify(resp)
            else:
                resp['success'] = False
                resp['message'] = 'scan does not exist'
                return jsonify(resp)
        else:
            scans = Scan.query.all()
            for scan in scans:
                resp = dict()
                resp['scan_id'] = scan.id
                resp['time_started'] = scan.created

                resp['scan_type'] = scan.scan_type
                resp['status'] = scan.status
                resp['scan_message'] = scan.scan_message
                scan_selenium_logs = ScanEvents.query.filter_by(scan_id=scan.id).first()
                if scan_selenium_logs:
                    resp['selenium_logs'] = scan_selenium_logs.scan_event_history
                else:
                    resp['selenium_logs'] = ''

                event = Events.query.filter_by(id=scan.event_id).first()
                if event:
                    resp['redtree_event_id'] = event.redtree_event_id
                    resp['nessus_event_status'] = event.event_status

                response.append(resp)
            return jsonify(response)


class NessusEventJobs(MethodView):

    def __init__(self):
        pass

    def get(self):

        data = dict()
        try:
            req = request.get_json()
        except Exception as e:
            print 'nessus_jobs() exception :: ',e

        try:
            redtree_event_id = req.get('event_id')
            event_list = list()
            # events = Events.query.filter_by(
            #     redtree_event_id=redtree_event_id).all()
            events = Events.query.filter(Events.redtree_event_id.\
                            in_(redtree_event_id)).all()

            for event in events:
                scans = Scan.query.filter_by(event_id=event.id).all()
                scan_status_queued = Scan.query.filter_by(status="Queued").\
                                        filter_by(event_id=event.id).count()
                scan_status_running = Scan.query.filter_by(status="Running").\
                                        filter_by(event_id=event.id).count()
                scan_status_complete = Scan.query.filter_by(status="Completed").\
                                        filter_by(event_id=event.id).count()
                scan_status_failed = Scan.query.filter_by(status="Failed").\
                                        filter_by(event_id=event.id).count()

                scan_list = list()
                for scan in scans:
                    scan_data = dict()

                    scan_data['scan_id'] = scan.id
                    scan_data['status'] = scan.status
                    scan_data['scan_name'] = scan.scan_name

                    scan_selenium_logs = ScanEvents.query.\
                                                    filter_by(scan_id=scan.id).all()

                    if scan_selenium_logs:
                        scan_data['scan_message'] = [event_logs.scan_event_history \
                                                for event_logs in scan_selenium_logs]
                    else:
                        scan_data['scan_message'] = 'scan is {}'.format(scan.status)

                    scan_list.append(scan_data)

                event_data = dict()
                event_data['event_id'] = event.id
                event_data['redtree_event_id'] = event.redtree_event_id
                event_data['event_status'] = event.event_status
                event_data['scans'] = scan_list
                event_data['message'] = 'scan is {}'.format(event.event_status)
                event_data['scan_status_queued'] = scan_status_queued 
                event_data['scan_status_running'] = scan_status_running 
                event_data['scan_status_completed'] = scan_status_complete
                event_data['scan_status_failed'] = scan_status_failed 

                event_list.append(event_data)

            return jsonify(event_list)

        except Exception as e:
            data['error'] = e
            data['status'] = None

        return jsonify(data)
