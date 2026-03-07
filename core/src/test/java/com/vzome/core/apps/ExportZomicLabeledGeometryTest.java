package com.vzome.core.apps;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.io.File;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.junit.Test;

public class ExportZomicLabeledGeometryTest
{
    @Test
    public void exportsLabeledPointsFromRegressionScript()
        throws Exception
    {
        File zomicFile = new File( "src/regression/files/Zomic/purpleStrutModel2/purpleStrutModel2.zomic" );
        assertTrue( zomicFile .exists() );

        Map<String, Object> exported = ExportZomicLabeledGeometry .exportLabeledGeometry( zomicFile );
        assertEquals( "antlr4", exported .get( "parser" ) );

        @SuppressWarnings("unchecked")
        List<Map<String, Object>> labeledPoints = (List<Map<String, Object>>) exported .get( "labeled_points" );
        assertTrue( labeledPoints .size() >= 10 );
        assertTrue( labeledPoints .stream() .anyMatch( point -> "pent.top.center" .equals( point .get( "label" ) ) ) );
        assertTrue( labeledPoints .stream() .anyMatch( point -> "pent.top.center" .equals( point .get( "source_label" ) ) ) );

        Set<Object> uniqueLabels = new HashSet<>();
        for ( Map<String, Object> point : labeledPoints ) {
            uniqueLabels .add( point .get( "label" ) );
        }
        assertEquals( labeledPoints .size(), uniqueLabels .size() );
    }
}
