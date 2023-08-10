"""View module for handling requests for serviceticket data"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket, Employee, Customer


class ServiceTicketView(ViewSet):
    """Honey Rae API servicetickets view"""

    def list(self, request):
        """Handle GET requests to get all servicetickets

        Returns:
            Response -- JSON serialized list of servicetickets
        """

        service_tickets = []


        if request.auth.user.is_staff:
            service_tickets = ServiceTicket.objects.all()

            if "status" in request.query_params:
                if request.query_params['status'] == "done":
                    service_tickets = service_tickets.filter(date_completed__isnull=False)

                if request.query_params['status'] == "all":
                    pass

        else:
            service_tickets = ServiceTicket.objects.filter(customer__user=request.auth.user)

        serialized = ServiceTicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)
    

    def update(self, request, pk=None):
        """"Handle pUT requests for single customer

        Returns: 
            Response -- NO response body. just 204 status code
        """

        #  Select the targeted ticket using primary key
        ticket = ServiceTicket.objects.get(pk=pk)

        #  Get the employee id from the client request
        employee_id = request.data['employee']

        # Select employee from database using that id

        assigned_employee = Employee.objects.get(pk=employee_id)

        # Assign the employee instance to the employee property of the ticket
        ticket.employee = assigned_employee

        # Save the updated ticket
        ticket.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    
    def create(self, request):
        """Handle POST requests for service tickets

        Returns:
            Response: JSON serialized representation of newly created service ticket
        """
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data['description']
        new_ticket.emergency = request.data['emergency']
        new_ticket.save()

        serialized = ServiceTicketSerializer(new_ticket, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single serviceticket

        Returns:
            Response -- JSON serialized serviceticket record
        """

        serviceticket = ServiceTicket.objects.get(pk=pk)
        serialized = ServiceTicketSerializer(serviceticket, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, pk=None):
        """Handle DELETE Requests for serviec tickets

        returns
            Response: none with a 204 code
        """

        service_ticket = ServiceTicket.objects.get(pk=pk)
        service_ticket.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)
    



class TicketEmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id', 'full_name', 'specialty')

class TicketCustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ('id', 'full_name', 'address')



class ServiceTicketSerializer(serializers.ModelSerializer):
    """JSON serializer for servicetickets"""
    employee = TicketEmployeeSerializer(many=False)
    customer = TicketCustomerSerializer(many=False)
    class Meta:
        model = ServiceTicket
        fields = ( 'id', 'description', 'emergency', 'date_completed', 'employee', 'customer' )
        depth = 2