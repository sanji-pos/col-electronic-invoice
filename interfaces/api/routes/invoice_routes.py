from fastapi import APIRouter, HTTPException, status
from domain.dtos import InvoiceDto, CreditNoteDto
from application.use_cases import CreateInvoiceCase, CreateNoteCase
from domain.database import dbClient
from bson.objectid import ObjectId
 
router = APIRouter(
    prefix="/api/invoice",
    tags=["invoice"]
)

@router.post("/create_invoice")
def create(request: InvoiceDto):
    try:
        electronicCertificate = dbClient["electronic-certificates"].find_one({
            "_id": ObjectId(request.ElectronicCertificateId)
        })
        create_invoice = CreateInvoiceCase(request, electronicCertificate["certificatePassword"], electronicCertificate["certificateBase64"])
        return create_invoice.send()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear la factura: " + str(e))
    
@router.post("/send_test")
def create(request: InvoiceDto):
    try:
        electronicCertificate = dbClient["electronic-certificates"].find_one({
            "_id": ObjectId(request.ElectronicCertificateId)
        })
        create_invoice = CreateInvoiceCase(request, electronicCertificate["certificatePassword"], electronicCertificate["certificateBase64"])
        return create_invoice.send_test()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear la factura: " + str(e))

@router.post("/create_credit_note")
def create(request: CreditNoteDto):
    try:
        electronicCertificate = dbClient["electronic-certificates"].find_one({
            "_id": ObjectId(request.ElectronicCertificateId)
        })
        create_note = CreateNoteCase(request, electronicCertificate["certificatePassword"], electronicCertificate["certificateBase64"])
        return create_note.start()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear la factura: " + str(e))